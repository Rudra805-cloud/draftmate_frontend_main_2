from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.party import CaseParty
from app.models.advocate import CaseAdvocate
from app.models.hearing import CaseHearing as CaseHearingModel
from app.models.judge import CaseJudge
from app.models.order import CaseOrder
from app.schemas.case import CaseOrderItem

from app.providers.ecourts import ECourtsProvider
from app.repositories.case_repository import CaseRepository

from app.schemas.case import (
    CaseHearing,
    CaseParties,
    CaseAdvocates,
    CaseJudges,
    CaseResponse,
    CourtInfo,
    HearingHistoryItem,
)

from app.services.case_mapper import map_provider_case, parse_date


class CaseService:
    def __init__(self):
        self.provider = ECourtsProvider()

    async def get_case(
        self,
        db: Session,
        cnr: str,
    ) -> CaseResponse:

        response = await self.provider.get_case(cnr)

        print("ECourts Case Response:")
        print(response)

        # Extract actual case data from provider
        case_data = (
            response.get("data", {}).get("courtCaseData")
            or response.get("courtCaseData")
            or response
        )

        # Get existing case from DB
        case = CaseRepository.get_by_cnr(db, cnr)

        # Create new case if it does not exist
        if not case:
            case = map_provider_case(case_data)
            case = CaseRepository.create(db, case)

        # Update existing case
        else:
            case.case_number = (
                case_data.get("caseNumber")
                or case_data.get("registrationNumber")
                or case_data.get("filingNumber")
                or case.case_number
            )

            case.case_type = case_data.get("caseType") or case.case_type
            case.status = case_data.get("caseStatus") or case.status

            case.state = (
                case_data.get("state") or case_data.get("stateCode") or case.state
            )

            case.district = (
                case_data.get("district")
                or case_data.get("districtCode")
                or case.district
            )

            case.court_name = case_data.get("courtName") or case.court_name

            case.filing_date = (
                parse_date(case_data.get("filingDate")) or case.filing_date
            )

            case.registration_date = (
                parse_date(case_data.get("registrationDate")) or case.registration_date
            )

            case.first_hearing_date = (
                parse_date(case_data.get("firstHearingDate")) or case.first_hearing_date
            )

            case.next_hearing_date = (
                parse_date(case_data.get("nextHearingDate")) or case.next_hearing_date
            )

            case.last_hearing_date = (
                parse_date(case_data.get("lastHearingDate")) or case.last_hearing_date
            )

            case.decision_date = (
                parse_date(case_data.get("decisionDate")) or case.decision_date
            )

            case = CaseRepository.update(db, case)

        # Save related case data
        self._save_parties(db, case, case_data)
        self._save_advocates(db, case, case_data)
        self._save_judges(db, case, case_data)
        self._save_hearings(db, case, case_data)
        self._save_orders(db, case, case_data)
        # Build API response, including hearing history from DB
        return self._build_response(db, case, case_data)

    # =========================================================
    # PARTIES
    # =========================================================

    def _save_parties(
        self,
        db: Session,
        case: Case,
        data: dict,
    ) -> None:

        db.query(CaseParty).filter(CaseParty.case_id == case.id).delete()

        petitioners = data.get("petitioners") or []
        respondents = data.get("respondents") or []

        for party in petitioners:
            name = party.get("name") if isinstance(party, dict) else party

            if name:
                db.add(
                    CaseParty(
                        case_id=case.id,
                        name=name,
                        party_type="PETITIONER",
                    )
                )

        for party in respondents:
            name = party.get("name") if isinstance(party, dict) else party

            if name:
                db.add(
                    CaseParty(
                        case_id=case.id,
                        name=name,
                        party_type="RESPONDENT",
                    )
                )

        db.commit()

    # =========================================================
    # ADVOCATES
    # =========================================================

    def _save_advocates(
        self,
        db: Session,
        case: Case,
        data: dict,
    ) -> None:

        db.query(CaseAdvocate).filter(CaseAdvocate.case_id == case.id).delete()

        petitioner_advocates = data.get("petitionerAdvocates") or []
        respondent_advocates = data.get("respondentAdvocates") or []

        for advocate in petitioner_advocates:
            name = advocate.get("name") if isinstance(advocate, dict) else advocate

            if name:
                db.add(
                    CaseAdvocate(
                        case_id=case.id,
                        name=name,
                        party_type="PETITIONER",
                    )
                )

        for advocate in respondent_advocates:
            name = advocate.get("name") if isinstance(advocate, dict) else advocate

            if name:
                db.add(
                    CaseAdvocate(
                        case_id=case.id,
                        name=name,
                        party_type="RESPONDENT",
                    )
                )

        db.commit()

    # =========================================================
    # JUDGES
    # =========================================================

    def _save_judges(
        self,
        db: Session,
        case: Case,
        data: dict,
    ) -> None:

        db.query(CaseJudge).filter(CaseJudge.case_id == case.id).delete()

        judges = data.get("judges") or []

        for judge in judges:
            name = judge.get("name") if isinstance(judge, dict) else judge

            if name:
                db.add(
                    CaseJudge(
                        case_id=case.id,
                        name=name,
                    )
                )

        db.commit()

    # =========================================================
    # HEARING HISTORY
    # =========================================================

    def _save_hearings(
        self,
        db: Session,
        case: Case,
        data: dict,
    ) -> None:

        # MVP approach: replace saved history with the latest
        # hearing history returned by the provider.
        db.query(CaseHearingModel).filter(CaseHearingModel.case_id == case.id).delete()

        hearings = data.get("historyOfCaseHearings") or []

        for hearing in hearings:
            business_on_date = parse_date(hearing.get("businessOnDate"))
            hearing_date = parse_date(hearing.get("hearingDate"))

            # Skip records without either date.
            if not business_on_date and not hearing_date:
                continue

            db.add(
                CaseHearingModel(
                    case_id=case.id,
                    business_on_date=business_on_date,
                    hearing_date=hearing_date,
                    purpose=hearing.get("purposeOfListing"),
                    judge=hearing.get("judge"),
                )
            )

        db.commit()

    #

    def _save_orders(
        self,
        db: Session,
        case: Case,
        data: dict,
    ) -> None:

        # Replace existing orders with the latest provider data.
        db.query(CaseOrder).filter(CaseOrder.case_id == case.id).delete()

        orders = []

        # Interim orders
        for item in data.get("interimOrders") or []:
            orders.append(
                {
                    "order_date": item.get("orderDate"),
                    "title": item.get("description") or "Interim Order",
                    "order_type": "INTERIM",
                    "file_name": item.get("fileName"),
                    "content_url": item.get("orderUrl"),
                    "description": item.get("description"),
                }
            )

        # Final orders / judgments
        for item in data.get("judgmentOrders") or []:
            orders.append(
                {
                    "order_date": item.get("orderDate"),
                    "title": item.get("orderType") or "Judgment",
                    "order_type": item.get("orderType") or "JUDGMENT",
                    "file_name": item.get("fileName"),
                    "content_url": item.get("orderUrl"),
                    "description": item.get("description"),
                }
            )

        for item in orders:
            db.add(
                CaseOrder(
                    case_id=case.id,
                    order_date=parse_date(item["order_date"]),
                    title=item["title"],
                    order_type=item["order_type"],
                    file_name=item["file_name"],
                    content_url=item["content_url"],
                    description=item["description"],
                )
            )

        db.commit()

    # =========================================================
    # BUILD RESPONSE
    # =========================================================

    @staticmethod
    def _build_response(
        db: Session,
        case: Case,
        data: dict,
    ) -> CaseResponse:

        petitioners = data.get("petitioners") or []
        respondents = data.get("respondents") or []
        petitioner_advocates = data.get("petitionerAdvocates") or []
        respondent_advocates = data.get("respondentAdvocates") or []
        judges = data.get("judges") or []

        # Normalize petitioners
        if petitioners and isinstance(petitioners[0], dict):
            petitioners = [p.get("name", "") for p in petitioners]

        # Normalize respondents
        if respondents and isinstance(respondents[0], dict):
            respondents = [r.get("name", "") for r in respondents]

        # Normalize petitioner advocates
        if petitioner_advocates and isinstance(petitioner_advocates[0], dict):
            petitioner_advocates = [a.get("name", "") for a in petitioner_advocates]

        # Normalize respondent advocates
        if respondent_advocates and isinstance(respondent_advocates[0], dict):
            respondent_advocates = [a.get("name", "") for a in respondent_advocates]

        # Normalize judges
        if judges and isinstance(judges[0], dict):
            judges = [j.get("name", "") for j in judges]

        # Fetch hearing history from the database
        hearing_records = (
            db.query(CaseHearingModel)
            .filter(CaseHearingModel.case_id == case.id)
            .order_by(
                CaseHearingModel.business_on_date.asc().nulls_last(),
                CaseHearingModel.hearing_date.asc().nulls_last(),
                CaseHearingModel.id.asc(),
            )
            .all()
        )

        hearing_history = [
            HearingHistoryItem(
                business_on_date=hearing.business_on_date,
                hearing_date=hearing.hearing_date,
                purpose=hearing.purpose,
                judge=hearing.judge,
            )
            for hearing in hearing_records
        ]

        order_records = (
            db.query(CaseOrder)
            .filter(CaseOrder.case_id == case.id)
            .order_by(
                CaseOrder.order_date.asc().nulls_last(),
                CaseOrder.id.asc(),
            )
            .all()
        )

        orders = [
            CaseOrderItem(
                order_date=order.order_date,
                title=order.title,
                order_type=order.order_type,
                file_name=order.file_name,
                content_url=order.content_url,
                description=order.description,
            )
            for order in order_records
        ]

        # Build final API response
        return CaseResponse(
            cnr=case.cnr,
            case_number=case.case_number,
            case_type=case.case_type,
            status=case.status,
            court=CourtInfo(
                name=case.court_name,
                district=case.district,
                state=case.state,
                court_code=None,
            ),
            parties=CaseParties(
                petitioners=petitioners,
                respondents=respondents,
            ),
            advocates=CaseAdvocates(
                petitioner_advocates=petitioner_advocates,
                respondent_advocates=respondent_advocates,
            ),
            judges=CaseJudges(
                judges=judges,
            ),
            hearing=CaseHearing(
                next_date=case.next_hearing_date,
                last_date=case.last_hearing_date,
            ),
            hearing_history=hearing_history,
            orders=orders,
        )

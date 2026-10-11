import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { API_CONFIG } from '../services/endpoints';
import { toast } from 'sonner';

const api = API_CONFIG.ECOURTS;
const emptyFilters = {
    state_code: '', district_code: '', court_code: '',
    case_type: '', case_status: '', filing_year: ''
};

const Spinner = ({ className = 'text-sm' }) => (
    <span className={`inline-flex items-center gap-2 ${className}`}>
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        Loading...
    </span>
);

const CaseSearch = () => {
    const [query, setQuery] = useState('');
    const [filters, setFilters] = useState(emptyFilters);
    const [states, setStates] = useState([]);
    const [districts, setDistricts] = useState([]);
    const [complexes, setComplexes] = useState([]);
    const [courts, setCourts] = useState([]);
    const [results, setResults] = useState([]);
    const [tracked, setTracked] = useState([]);
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(false);
    const [statesLoading, setStatesLoading] = useState(true);
    const [trackedLoading, setTrackedLoading] = useState(false);
    const [locationLoading, setLocationLoading] = useState('');
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [actionCnr, setActionCnr] = useState('');
    const [activeTab, setActiveTab] = useState('search');
    const [addCnr, setAddCnr] = useState('');
    const [showAddCnr, setShowAddCnr] = useState(false);

    const sessionId = localStorage.getItem('session_id');
    const authConfig = sessionId ? { headers: { Authorization: `Bearer ${sessionId}` } } : {};
    const trackedCnrs = useMemo(() => new Set(tracked.map((item) => item.cnr)), [tracked]);

    useEffect(() => {
        loadStates();
        loadTracked();
    }, []);

    const loadStates = async () => {
        setStatesLoading(true);
        try {
            const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.STATES}`);
            setStates(data);
        } catch {
            toast.error('Unable to load court states.');
        } finally {
            setStatesLoading(false);
        }
    };

    const loadTracked = async () => {
        if (!sessionId) return;
        setTrackedLoading(true);
        try {
            const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.LIST_TRACKED}`, authConfig);
            setTracked(data);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Unable to load tracked cases.');
        } finally {
            setTrackedLoading(false);
        }
    };

    const locationChange = async (key, value) => {
        const next = { ...filters, [key]: value };
        setLocationLoading(key);
        if (key === 'state_code') {
            next.district_code = ''; next.court_code = '';
            setDistricts([]); setComplexes([]); setCourts([]);
            if (value) {
                try {
                    const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.DISTRICTS(value)}`);
                    setDistricts(data);
                } catch (error) {
                    toast.error(error.response?.data?.detail || 'Unable to load districts.');
                }
            }
        }
        if (key === 'district_code') {
            next.court_code = ''; setComplexes([]); setCourts([]);
            if (value && next.state_code) {
                try {
                    const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.COMPLEXES(next.state_code, value)}`);
                    setComplexes(data);
                } catch (error) {
                    toast.error(error.response?.data?.detail || 'Unable to load court complexes.');
                }
            }
        }
        if (key === 'court_code' && value && next.state_code && next.district_code) {
            try {
                const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.COURTS(next.state_code, next.district_code, value)}`);
                setCourts(data);
            } catch (error) {
                toast.error(error.response?.data?.detail || 'Unable to load courts.');
            }
        }
        setFilters(next);
        setLocationLoading('');
    };

    const searchCases = async (event) => {
        event.preventDefault();
        const searchTerm = query.trim();
        if (!searchTerm) {
            toast.error('Enter a CNR, case number, or party name before applying filters.');
            return;
        }
        setLoading(true);
        setActiveTab('search');
        try {
            const { data } = await axios.post(`${api.BASE_URL}${api.ENDPOINTS.SEARCH_CASES}`, {
                query: searchTerm,
                ...filters,
                filing_year: filters.filing_year ? Number(filters.filing_year) : null,
                page: 1,
                limit: 20
            });
            setResults(data.items || []);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Case search failed.');
        } finally {
            setLoading(false);
        }
    };

    const openDetails = async (cnr) => {
        setDetailsLoading(true);
        try {
            const { data } = await axios.get(`${api.BASE_URL}${api.ENDPOINTS.GET_CASE(cnr)}`);
            setDetails(data);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Unable to load case details.');
        } finally {
            setDetailsLoading(false);
        }
    };

    const track = async (cnr) => {
        if (!sessionId) return toast.error('Login is required to add a case.');
        setActionCnr(cnr);
        try {
            await axios.post(`${api.BASE_URL}${api.ENDPOINTS.TRACK_CASE(cnr)}`, {}, authConfig);
            toast.success('Case added to tracking.');
            await loadTracked();
            setActiveTab('tracked');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Unable to add case.');
        } finally {
            setActionCnr('');
        }
    };

    const addByCnr = async (event) => {
        event.preventDefault();
        const cnr = addCnr.trim().toUpperCase();
        if (!cnr) return toast.error('Enter a CNR number.');
        await track(cnr);
        setAddCnr('');
        setShowAddCnr(false);
    };

    const refresh = async (cnr) => {
        setActionCnr(cnr);
        try {
            await axios.post(`${api.BASE_URL}${api.ENDPOINTS.REFRESH_CASE(cnr)}`, {}, authConfig);
            toast.success('Case information refreshed.');
            await loadTracked();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Unable to refresh case.');
        } finally {
            setActionCnr('');
        }
    };

    const remove = async (cnr) => {
        setActionCnr(cnr);
        try {
            await axios.delete(`${api.BASE_URL}${api.ENDPOINTS.UNTRACK_CASE(cnr)}`, authConfig);
            toast.success('Case removed from tracking.');
            await loadTracked();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Unable to remove case.');
        } finally {
            setActionCnr('');
        }
    };

    const selectClass = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-700 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200';
    const fieldClass = `${selectClass} placeholder:text-slate-400`;

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white">
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <header className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">
                    <div>
                        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold uppercase tracking-wider text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300">
                            <span className="material-symbols-outlined text-sm">account_balance</span> e-Court workspace
                        </div>
                        <h1 className="text-3xl font-black tracking-tight sm:text-4xl">Case intelligence</h1>
                        <p className="mt-2 max-w-2xl text-slate-500 dark:text-slate-400">Search court records, review live case details, and keep important matters under watch.</p>
                    </div>
                    <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Tracked cases</p>
                        <p className="mt-1 text-2xl font-black text-indigo-600 dark:text-indigo-400">{tracked.length}</p>
                    </div>
                </header>

                <div className="mb-6 flex gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    {[['search', 'Search cases', 'search'], ['tracked', 'Added cases', 'bookmark']].map(([tab, label, icon]) => (
                        <button key={tab} onClick={() => setActiveTab(tab)} className={`flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-bold transition ${activeTab === tab ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'}`}>
                            <span className="material-symbols-outlined text-lg">{icon}</span>{label}
                        </button>
                    ))}
                    <button onClick={() => setShowAddCnr(true)} className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-indigo-700">
                        <span className="material-symbols-outlined text-lg">add</span><span className="hidden sm:inline">Add by CNR</span>
                    </button>
                </div>

                {activeTab === 'search' ? <section>
                    <form onSubmit={searchCases} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-7">
                        <div className="flex flex-col gap-3 sm:flex-row">
                            <div className="relative flex-1">
                                <span className="material-symbols-outlined absolute left-4 top-3.5 text-slate-400">search</span>
                                <input className={`${fieldClass} pl-12`} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="CNR, case number, petitioner, respondent..." />
                            </div>
                            <button disabled={loading || Boolean(locationLoading)} className="rounded-xl bg-indigo-600 px-7 py-3 font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60">{loading ? <Spinner /> : 'Search cases'}</button>
                        </div>
                        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                                    <select className={selectClass} value={filters.state_code} onChange={(e) => locationChange('state_code', e.target.value)} disabled={!query.trim() || statesLoading || Boolean(locationLoading)}><option value="">{!query.trim() ? 'Enter search first' : statesLoading ? 'Loading states...' : 'All states'}</option>{states.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}</select>
                                    <select className={selectClass} value={filters.district_code} onChange={(e) => locationChange('district_code', e.target.value)} disabled={!query.trim() || !filters.state_code || Boolean(locationLoading)}><option value="">{!query.trim() ? 'Enter search first' : locationLoading === 'state_code' ? 'Loading districts...' : 'All districts'}</option>{districts.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}</select>
                                    <select className={selectClass} value={filters.court_code} onChange={(e) => locationChange('court_code', e.target.value)} disabled={!query.trim() || !filters.district_code || Boolean(locationLoading)}><option value="">{!query.trim() ? 'Enter search first' : locationLoading === 'district_code' ? 'Loading court complexes...' : 'All court complexes'}</option>{complexes.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}</select>
                            <input className={fieldClass} placeholder="Case type" value={filters.case_type} disabled={!query.trim()} onChange={(e) => setFilters({ ...filters, case_type: e.target.value })} />
                            <input className={fieldClass} placeholder="Status (e.g. DISPOSED)" value={filters.case_status} disabled={!query.trim()} onChange={(e) => setFilters({ ...filters, case_status: e.target.value })} />
                            <input className={fieldClass} type="number" placeholder="Filing year" value={filters.filing_year} disabled={!query.trim()} onChange={(e) => setFilters({ ...filters, filing_year: e.target.value })} />
                        </div>
                        {courts.length > 0 && <p className="mt-4 text-xs text-slate-500">Available courts: {courts.map((item) => item.name).join(' · ')}</p>}
                    </form>

                    <div className="mt-8">
                        <div className="mb-4 flex items-center justify-between"><h2 className="text-xl font-black">Search results</h2><span className="text-sm text-slate-500">{results.length} found</span></div>
                        {loading ? <div className="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center dark:border-slate-800 dark:bg-slate-900"><Spinner className="justify-center font-bold" /></div> : results.length === 0 ? <div className="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center dark:border-slate-700 dark:bg-slate-900"><span className="material-symbols-outlined text-5xl text-slate-300">manage_search</span><p className="mt-3 font-bold">Start with a CNR or party name</p><p className="mt-1 text-sm text-slate-500">Use the filters above to narrow down court records.</p></div> : <div className="grid gap-4 lg:grid-cols-2">{results.map((item) => <article key={item.cnr} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
                            <div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">{item.case_type || 'Case'}</p><h3 className="mt-1 font-black">{item.case_number || item.cnr}</h3><p className="mt-1 text-xs text-slate-500">CNR: {item.cnr}</p></div><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{item.status || 'Unknown'}</span></div>
                            <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-500"><p><b className="block text-slate-400">Court</b>{item.court_code || 'Not available'}</p><p><b className="block text-slate-400">Next hearing</b>{item.next_hearing_date || 'Not scheduled'}</p></div>
                            <div className="mt-5 flex gap-4 border-t border-slate-100 pt-4 text-sm font-bold dark:border-slate-800"><button className="text-indigo-600 dark:text-indigo-400 disabled:opacity-60" onClick={() => openDetails(item.cnr)} disabled={Boolean(actionCnr) || detailsLoading}>{detailsLoading ? 'Loading...' : 'View details'}</button>{trackedCnrs.has(item.cnr) ? <span className="text-emerald-600">Added</span> : <button className="text-indigo-600 dark:text-indigo-400 disabled:opacity-60" onClick={() => track(item.cnr)} disabled={Boolean(actionCnr)}>{actionCnr === item.cnr ? 'Adding...' : 'Add to tracking'}</button>}</div>
                        </article>)}</div>}
                    </div>
                </section> : <section>
                    <div className="mb-4 flex items-center justify-between"><h2 className="text-xl font-black">Added cases</h2><button onClick={loadTracked} disabled={trackedLoading} className="text-sm font-bold text-indigo-600 disabled:opacity-60">{trackedLoading ? <Spinner /> : 'Refresh list'}</button></div>
                    {trackedLoading ? <div className="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center dark:border-slate-800 dark:bg-slate-900"><Spinner className="justify-center font-bold" /></div> : tracked.length === 0 ? <div className="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center dark:border-slate-700 dark:bg-slate-900"><span className="material-symbols-outlined text-5xl text-slate-300">bookmark_add</span><p className="mt-3 font-bold">No tracked cases yet</p><p className="mt-1 text-sm text-slate-500">Search for a case and add it to your watchlist.</p></div> : <div className="grid gap-4 lg:grid-cols-2">{tracked.map((item) => <article key={item.cnr} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"><div className="flex justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-wider text-indigo-600">Tracked case</p><h3 className="mt-1 font-black">{item.case_number || item.cnr}</h3><p className="mt-1 text-xs text-slate-500">{item.cnr}</p></div><span className="h-fit rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">{item.status || 'Active'}</span></div><p className="mt-4 text-sm text-slate-500">{item.court_name || item.court_code || 'Court unavailable'} · Next hearing: {item.next_hearing_date || 'Not scheduled'}</p><div className="mt-5 flex gap-4 border-t border-slate-100 pt-4 text-sm font-bold dark:border-slate-800"><button className="text-indigo-600" onClick={() => openDetails(item.cnr)}>Details</button><button className="text-indigo-600" onClick={() => refresh(item.cnr)} disabled={actionCnr === item.cnr}>{actionCnr === item.cnr ? 'Refreshing...' : 'Refresh'}</button><button className="text-rose-600" onClick={() => remove(item.cnr)} disabled={actionCnr === item.cnr}>{actionCnr === item.cnr ? 'Working...' : 'Remove'}</button></div></article>)}</div>}
                </section>}
            </div>

            {(details || detailsLoading) && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4" onClick={() => setDetails(null)}><div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl dark:bg-slate-900 sm:p-8" onClick={(e) => e.stopPropagation()}>{detailsLoading ? <p className="py-16 text-center font-bold"><Spinner className="justify-center" /></p> : <><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-wider text-indigo-600">Case details</p><h2 className="mt-1 text-2xl font-black">{details.case_number || details.cnr}</h2><p className="mt-1 text-sm text-slate-500">{details.cnr}</p></div><button className="text-slate-400" onClick={() => setDetails(null)}><span className="material-symbols-outlined">close</span></button></div><div className="mt-6 grid gap-4 sm:grid-cols-2">{[['Status', details.status], ['Case type', details.case_type], ['Court', details.court?.name], ['State', details.court?.state], ['District', details.court?.district], ['Next hearing', details.hearing?.next_date]].map(([label, value]) => <div key={label} className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800"><p className="text-xs font-bold uppercase tracking-wider text-slate-400">{label}</p><p className="mt-1 font-bold">{value || 'Not available'}</p></div>)}</div><div className="mt-6 grid gap-5 sm:grid-cols-2"><div><h3 className="font-black">Petitioners</h3><p className="mt-2 text-sm text-slate-500">{details.parties?.petitioners?.join(', ') || 'Not available'}</p></div><div><h3 className="font-black">Respondents</h3><p className="mt-2 text-sm text-slate-500">{details.parties?.respondents?.join(', ') || 'Not available'}</p></div></div><button onClick={() => track(details.cnr)} disabled={Boolean(actionCnr)} className="mt-7 w-full rounded-xl bg-indigo-600 py-3 font-bold text-white hover:bg-indigo-700 disabled:opacity-60">{actionCnr ? <Spinner className="justify-center" /> : trackedCnrs.has(details.cnr) ? 'Case already tracked' : 'Add case to tracking'}</button></>}</div></div>}
            {showAddCnr && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4" onClick={() => setShowAddCnr(false)}><form onSubmit={addByCnr} onClick={(e) => e.stopPropagation()} className="w-full max-w-md rounded-3xl bg-white p-7 shadow-2xl dark:bg-slate-900"><div className="flex items-start justify-between"><div><p className="text-xs font-bold uppercase tracking-wider text-indigo-600">Track a case</p><h2 className="mt-1 text-2xl font-black">Add by CNR</h2></div><button type="button" onClick={() => setShowAddCnr(false)} disabled={Boolean(actionCnr)} className="text-slate-400 disabled:opacity-60"><span className="material-symbols-outlined">close</span></button></div><p className="mt-3 text-sm text-slate-500">Enter the 16-character CNR to fetch and add the case.</p><input autoFocus value={addCnr} onChange={(e) => setAddCnr(e.target.value)} disabled={Boolean(actionCnr)} placeholder="Example: MNHC010014882019" className={`${fieldClass} mt-5`} /><button disabled={Boolean(actionCnr)} className="mt-4 w-full rounded-xl bg-indigo-600 py-3 font-bold text-white hover:bg-indigo-700 disabled:opacity-60">{actionCnr ? <Spinner className="justify-center" /> : 'Add case'}</button></form></div>}
        </div>
    );
};

export default CaseSearch;

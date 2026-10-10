class CaseNotFoundError(Exception):
    pass


class ProviderAuthenticationError(Exception):
    pass


class ProviderRateLimitError(Exception):
    pass


class ProviderUnavailableError(Exception):
    pass

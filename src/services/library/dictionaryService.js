const API_BASE_URL = "/api/v1/library/terms";

const handleResponse = async (response, message) => {
  if (!response.ok) {
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return response.json();
};

export const dictionaryService = {
  searchTerms: async (query, page = 1, limit = 20) => {
    const params = new URLSearchParams({
      query: (query || "").trim(),
      page: String(page),
      limit: String(limit),
    });

    const response = await fetch(`${API_BASE_URL}?${params.toString()}`);
    return handleResponse(response, "Failed to search terms");
  },

  getTermById: async (termId) => {
    const response = await fetch(`${API_BASE_URL}/${termId}`);
    return handleResponse(response, "Failed to fetch term details");
  },
};
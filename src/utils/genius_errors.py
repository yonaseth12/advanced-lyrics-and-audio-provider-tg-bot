from requests.exceptions import HTTPError


def genius_error_user_message(exc: HTTPError) -> str:
	# print("...", exc, "...")
	status = exc.response.status_code if exc.response is not None else None
	if status in (401, 403):
		return (
			"Could not reach Genius: the API token is invalid or expired. "
			"Create a client access token at https://genius.com/api-clients and set TOKEN_GENIUS in your .env."
		)
	if status == 429:
		return "Genius rate limit reached. Please wait a minute and try again."
	if status is not None and 500 <= status <= 599:
		return "Genius is currently having server issues. Please try again later."
	if status is not None:
		return f"Genius request failed (HTTP {status}). Please verify your API token and try again."
	return "The lyrics service is temporarily unavailable. Please try again later."

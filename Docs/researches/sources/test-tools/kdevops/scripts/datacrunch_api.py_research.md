<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_api.py -->
# sources/test-tools/kdevops/scripts/datacrunch_api.py

Purpose: provides the shared low-level DataCrunch API client for kdevops scripts. It handles OAuth2 client-credentials token retrieval, authenticated GET and POST requests, and high-level list helpers for instance types, images, locations, instances, SSH keys, and instance availability.

Important APIs and functions: `get_api_key()` delegates to `datacrunch_credentials`; `get_access_token()` reads credentials, posts form data to `/oauth2/token`, caches `_access_token_cache`, and supports `force_refresh`; `make_api_request()` performs authenticated GET with one 401 retry; `make_api_post()` sends JSON POSTs; `list_instance_types()`, `list_images()`, `list_locations()`, `list_instances()`, `list_ssh_keys()`, and `get_instance_availability()` normalize common response shapes. `main()` is a manual connectivity smoke test.

Control flow: callers either request a token directly or call a high-level function, which obtains a token if needed, makes an HTTP request, decodes JSON, normalizes list-bearing objects, and returns `None` on errors. The manual CLI checks credentials, token acquisition, then several endpoints.

State and persistence: no files are written. The only state is the in-process access token cache; credentials are read from the credentials module.

Dependencies and integration: uses standard-library `urllib`, `json`, `socket`, and local `datacrunch_credentials.py`. It is imported by `generate_datacrunch_kconfig.py` and `datacrunch_ssh_keys.py`.

Risks: cached tokens are not expiration-aware, so failed requests rely on 401 refresh. Error handling prints to stderr and suppresses bodies for GET retry failures. API schema drift can yield empty defaults. Test signals include mocking `urllib.request.urlopen`, testing list response normalization, 401 refresh behavior, missing credentials, and malformed JSON handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_api.py -->

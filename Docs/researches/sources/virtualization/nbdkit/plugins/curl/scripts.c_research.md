# File Research: sources/virtualization/nbdkit/plugins/curl/scripts.c

Implements dynamic header and cookie scripts for the curl plugin.

Key behavior:
- Maintains cached output from `header-script` and `cookie-script`.
- Re-runs scripts when first used or when `*-renew` intervals expire.
- Protects script state with a process-wide mutex.
- Injects `url` and `iteration` shell variables into generated shell commands.
- Captures script stderr into a temporary file and reports the first error line through `nbdkit_error`.
- Duplicates global header lists per easy handle because libcurl does not copy `CURLOPT_HTTPHEADER`.
- Sets cookies via `CURLOPT_COOKIE`, which libcurl copies internally.

Platform behavior:
- Non-Windows uses `mkstemp`, `open_memstream`, `popen`, `getline`, shell quoting, and curl slists.
- Windows build stubs out script support and reports `NOT_IMPLEMENTED_ON_WINDOWS` when scripts are configured.

Notable details:
- `scripts_unload` frees cached curl header slists and cookie strings.
- Empty header lines and empty cookie output are ignored.

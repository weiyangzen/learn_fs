<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py -->
# sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py

## Purpose
This Python script checks the rcloud service health endpoint and prints raw JSON, human-readable interpretation, troubleshooting steps, and suggested follow-up API calls. It is used by the Makefile after service installation and by the `rcloud-status` target.

## Important APIs and Functions
`check_health(endpoint)` constructs `<endpoint>/api/v1/health`, performs a `urllib.request.urlopen` with a five-second timeout, parses JSON, and returns `(success, data, message)`. `explain_health_status(data)` maps the `status` field to explanatory text and includes the server version. `main()` parses an optional endpoint argument, prints diagnostics, calls the checker, and returns exit status `0` or `1`.

## Control Flow
The script defaults to `http://localhost:8765`. On failure it prints service, socket, and journalctl troubleshooting hints. On success it prints the raw response, explanation, and curl examples for `/api/v1/vms`, `/api/v1/images`, `/api/v1/status`, and `/metrics`.

## State, Persistence, and Dependencies
There is no persistent local state. It uses only Python standard library modules: `json`, `sys`, `urllib.request`, and `urllib.error`. It depends on the rcloud server returning JSON with at least `status` and `version`.

## Risks and Test Signals
The script currently includes non-ASCII symbols in output, which can be awkward in constrained logs. `urllib.error.HTTPError` is a subclass of `URLError`, but the code catches `URLError` first, so HTTP-specific handling may be bypassed. The test signal is process exit status plus the parsed health JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py -->

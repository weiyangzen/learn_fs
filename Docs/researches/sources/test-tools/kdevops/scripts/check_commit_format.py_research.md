# sources/test-tools/kdevops/scripts/check_commit_format.py

Purpose: validates latest Git commit message formatting around `Generated-by: Claude AI` and `Signed-off-by:`.

Important APIs/types/functions: `subprocess.run(["git","log","-1","--pretty=format:%B"])`, `check_commit_format`, line scanning, issue list, and CLI `main`.

Control flow: reads latest commit message, finds Generated-by and Signed-off-by lines, requires Signed-off-by to immediately follow Generated-by when present, prints detailed diagnostics and returns nonzero on problems.

State/persistence behavior: read-only Git metadata inspection.

Dependencies/integration: intended for CI or local commit hooks.

Risks/test signals: only checks the latest commit and exact prefix `Generated-by: Claude AI`; multiple Signed-off-by lines collapse to last seen. Test signals are exit code 0/1 and printed offending lines.

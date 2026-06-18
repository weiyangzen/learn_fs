# File Research: sources/virtualization/nvme-cli/tests/nvme_error_log_test.py

Python integration test for error log retrieval.

Flow:
- Calls shared `get_error_log`.
- The shared helper runs `nvme error-log`, parses normal text output, and checks the printed entry count against the number of `Entry[...]` lines.

Role:
- Verifies command success and a basic consistency property of human-readable output.

# File Research: sources/virtualization/nvme-cli/tests/nvme_smart_log_test.py

Python integration test for SMART log retrieval.

Flow:
- Runs controller-wide SMART log using namespace ID `0xFFFFFFFF`.
- Reads Identify Controller `lpa`.
- If SMART/health information is namespace-specific, iterates namespaces and runs SMART log for each.
- Expects all invoked commands to succeed.

Dependencies:
- Uses shared `get_smart_log`, `get_nsid_list`, and numeric conversion helper.

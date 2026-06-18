# File Research: sources/virtualization/nvme-cli/tests/nvme_lba_status_log_test.py

Python integration test for LBA Status Log.

Flow:
- Skips unless OACS bit 9 indicates Get LBA Status support.
- Runs `nvme lba-status-log <controller>`.
- Expects success.

Role:
- Smoke test for the log-page counterpart to Get LBA Status.

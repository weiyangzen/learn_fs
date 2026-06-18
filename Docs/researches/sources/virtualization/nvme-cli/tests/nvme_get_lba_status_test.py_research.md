# File Research: sources/virtualization/nvme-cli/tests/nvme_get_lba_status_test.py

Python integration test for Get LBA Status.

Flow:
- Skips unless Identify Controller OACS bit 9 indicates Get LBA Status support.
- Runs `nvme get-lba-status` with namespace, start LBA 0, max DW 1, action `0x11`, and range length 1.
- Expects success.

Notes:
- The command uses `self.ctrl` and passes `--namespace-id` as `self.ns1`, which is a device path string from config rather than numeric `1`; this is worth checking against command parser expectations.

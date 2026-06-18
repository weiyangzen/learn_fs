# File Research: sources/virtualization/nvme-cli/tests/nvme_ctrl_reset_test.py

Python integration test for controller reset.

Flow:
- Runs `nvme reset <controller>`.
- After reset, runs simple namespace I/O to verify queues are usable again.

Dependencies:
- Uses shared `TestNVMe.run_ns_io`.

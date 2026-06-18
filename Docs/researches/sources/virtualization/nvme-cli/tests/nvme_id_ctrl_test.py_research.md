# File Research: sources/virtualization/nvme-cli/tests/nvme_id_ctrl_test.py

Python integration test for Identify Controller.

Flow:
- Runs normal `nvme id-ctrl <controller>`.
- Runs vendor-specific `nvme id-ctrl --vendor-specific <controller>`.
- Expects both to succeed.

Role:
- Exercises both standard and vendor-specific identify controller output paths.

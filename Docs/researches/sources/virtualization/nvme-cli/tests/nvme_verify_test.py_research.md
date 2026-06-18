# File Research: sources/virtualization/nvme-cli/tests/nvme_verify_test.py

Python integration test for NVMe Verify.

Flow:
- Checks Optional NVM Command Support bit 7 for Verify.
- Skips if unsupported.
- Runs `nvme verify <controller> --namespace-id=1 --start-block=0 --block-count=0`.
- Expects success.

Role:
- Capability-gated smoke test for the Verify command.

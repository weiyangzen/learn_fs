# File Research: sources/virtualization/nvme-cli/tests/nvme_flush_test.py

Python integration test for Flush.

Flow:
- Runs `nvme flush <controller> --namespace-id=1`.
- Expects success.

Role:
- Simple command smoke test against the configured controller/default namespace.

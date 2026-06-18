# File Research: sources/virtualization/nvme-cli/tests/nvme_dsm_test.py

Python integration test for Dataset Management.

Flow:
- Sets namespace ID 1, start block 0, and range 0.
- Runs `nvme dsm <controller> --namespace-id=1 --blocks=0 --slbs=0`.
- Expects success.

Notes:
- The docstring says verify in one helper comment, but the command is DSM.

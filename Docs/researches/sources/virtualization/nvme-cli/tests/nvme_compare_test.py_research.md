# File Research: sources/virtualization/nvme-cli/tests/nvme_compare_test.py

Python integration test for the NVMe Compare command.

Flow:
- Inherits `TestNVMeIO`.
- Skips if Optional NVM Command Support does not advertise Compare.
- Writes a patterned block at start block 1023.
- Compares against a different pattern and expects failure.
- Compares against the written pattern and expects success.
- Handles separate metadata namespaces by creating metadata buffers and passing `--metadata-size`/`--metadata`.

Dependencies:
- Uses `TestNVMeIO` for PI/metadata-aware data size and write command construction.

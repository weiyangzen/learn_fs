# File Research: sources/virtualization/nvme-cli/tests/nvme_writeuncor_test.py

Python integration test for Write Uncorrectable.

Flow:
- Inherits `TestNVMeIO`.
- Skips unless Optional NVM Command Support bit 1 is set.
- Reads a block successfully.
- Issues `nvme write-uncor` at start block 1023.
- Expects a subsequent read to fail.
- Writes valid data and then expects read to succeed again.

Risk:
- Intentionally marks media logical block state uncorrectable during the test.

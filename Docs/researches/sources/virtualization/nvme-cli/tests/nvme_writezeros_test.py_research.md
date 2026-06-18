# File Research: sources/virtualization/nvme-cli/tests/nvme_writezeros_test.py

Python integration test for Write Zeroes.

Flow:
- Inherits `TestNVMeIO`.
- Writes patterned data to start block 1023.
- Reads it back and verifies it matches.
- Runs `nvme write-zeroes` on the same block.
- Reads again and verifies data matches a locally generated zero-filled file.
- Handles separate metadata buffer setup for writes/reads.

Role:
- End-to-end validation that write-zeroes changes the target block to zeros.

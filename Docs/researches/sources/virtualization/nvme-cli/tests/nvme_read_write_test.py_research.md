# File Research: sources/virtualization/nvme-cli/tests/nvme_read_write_test.py

Python integration test for read/write round trip.

Flow:
- Inherits `TestNVMeIO`.
- Writes a patterned file to start block 1023.
- Reads the block back into another file.
- Compares the files with `filecmp.cmp`.
- Creates metadata buffers when active namespace uses separate metadata.

Dependencies:
- Uses `TestNVMeIO` to select data size and PI/metadata options.

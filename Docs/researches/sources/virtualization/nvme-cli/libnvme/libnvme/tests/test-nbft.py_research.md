# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-nbft.py

This Python unittest verifies NBFT binary parsing through the Python bindings.

Core behavior:
- Defines an expected NBFT dictionary with discovery, HFI, host, and subsystem entries.
- Creates `GlobalCtx`, sets debug log level, and calls `nvme.nbft_get(ctx, args.filename)`.
- Asserts exact equality with expected data.
- Uses argparse to accept `--filename`, preserving unittest args.

Integration role:
- Tests libnvme NBFT parser output shape and Python conversion behavior.

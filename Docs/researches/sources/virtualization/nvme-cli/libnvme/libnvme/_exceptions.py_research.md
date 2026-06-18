# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/_exceptions.py

This Python file defines libnvme exception classes.

Classes:
- `NvmeError`: base exception storing `errno` and `message`, with formatted exception text.
- `ConnectError`
- `DisconnectError`
- `DiscoverError`
- `NotConnectedError`, defaulting to errno 0 and message `Not connected`.

Integration role:
- Used by Python bindings to expose typed errors for connection, disconnection, discovery, and disconnected-state failures.
- Tested by `test-objects.py`.

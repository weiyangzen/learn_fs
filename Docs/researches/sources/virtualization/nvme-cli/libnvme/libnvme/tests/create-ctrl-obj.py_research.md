# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/create-ctrl-obj.py

This small Python test creates a libnvme controller object.

Core behavior:
- Imports `libnvme.nvme`.
- Creates `GlobalCtx` and sets log level to debug.
- Creates a discovery controller over loop transport with address `127.0.0.1` and service `8009`.

Integration role:
- Smoke test for Python controller object construction with a dictionary of fabrics parameters.

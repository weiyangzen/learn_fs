# File Research: sources/virtualization/nvme-cli/libnvme/test/tree.py

This is a minimal Python binding smoke script. It imports `libnvme`, creates `libnvme.nvme_root()`, and prints every host, subsystem, and controller reachable through the Python object model.

Behavior:
- Iterates `r.hosts()`.
- For each host, iterates `h.subsystems()`.
- For each subsystem, iterates `s.controllers()`.

Integration:
- Exercises generated/manual Python bindings enough to verify traversal methods are callable and printable.
- It depends on the runtime environment’s observable NVMe topology; on systems with no devices it may produce no topology output but still validates import/root creation.

Risk and maintenance notes:
- No assertions are present; this is diagnostic/smoke coverage rather than a strict unit test.
- Output depends on host state.

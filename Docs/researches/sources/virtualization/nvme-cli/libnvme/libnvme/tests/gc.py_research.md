# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/gc.py

This Python test exercises garbage collection and object lifetime ordering.

Core behavior:
- Creates global context, host, and ten loop discovery controller objects.
- Iterates host subsystems and namespaces.
- Clears `ctx` and `host` before controller/subsystem objects.
- Forces `gc.collect()`.
- Then clears controller and remaining object references.

Purpose:
- Guards against segmentation faults when Python/SWIG objects are destroyed in an order where child objects outlive parent wrappers.

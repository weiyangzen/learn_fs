# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-objects.py

This Python unittest suite covers hardware-free object creation, properties, constants, exceptions, and helper functions.

Coverage:
- Constants: discovery subsystem name and discovery log LID.
- `GlobalCtx`: construction, context manager, hosts iterator, topology refresh, log-level values.
- `Host`: construction with hostnqn, hostid, hostsymname; writable `hostsymname`; default DHCHAP host key; subsystem iteration; string representation; context manager.
- `Ctrl`: loop and tcp construction, property access, connected/name defaults, context manager, namespaces iterator, discovery/persistent/unique flags, multiple controllers in one context.
- Exceptions: importability, inheritance, errno/message behavior, `NotConnectedError` defaults.
- Error handling: disconnect/discover on unconnected controller raises `NotConnectedError`.
- Helper functions: `read_hostnqn()` and `read_hostid()` return string or None.

Integration role:
- Main regression suite for Python binding object semantics without requiring real NVMe hardware.

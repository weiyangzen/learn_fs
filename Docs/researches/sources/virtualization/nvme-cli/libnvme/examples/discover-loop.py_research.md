# File Research: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.py

This Python example performs recursive NVMe-oF discovery using libnvme Python bindings.

Core behavior:
- Creates `GlobalCtx`, `Host`, and an initial TCP discovery controller for `127.0.0.1:4420`.
- `discover()` connects a controller, prints support for discovery log-page options, retrieves the discovery log, and recurses through discovery referrals.
- Limits recursion to 8 levels.
- Handles `ConnectError`, `DiscoverError`, and possible failures reading supported log pages.
- Prints discovered NVM and discovery subsystem records.
- Finally prints subsystems and controllers known to the host.

Integration role:
- Demonstrates high-level Python bindings for controller connection, log-page discovery, context managers, recursive discovery, and exception handling.

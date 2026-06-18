# File Research: sources/virtualization/nvme-cli/fabrics.c

This is the nvme-cli front-end implementation for NVMe over Fabrics commands. It parses CLI options, prepares libnvme/libnvmf contexts, loads JSON/volatile/NBFT/discovery configuration, and delegates the actual fabrics operations to libnvme.

Main commands:
- `fabrics_discovery()`: implements discovery and connect-all style flows. It supports explicit endpoints, existing discovery controller devices, NBFT discovery, JSON config, volatile runtime config, and `/etc/nvme/discovery.conf`.
- `fabrics_connect()`: validates required connection fields, loads config if requested, creates a fabrics context, and connects via `libnvmf_connect()` or JSON config connection.
- `fabrics_disconnect()`: disconnects by NQN or device name after scanning current topology.
- `fabrics_disconnect_all()`: disconnects non-PCIe fabrics controllers, optionally filtered by transport.
- `fabrics_config()`: reads, scans, modifies, updates, and dumps JSON configuration.
- `fabrics_dim()`: performs Discovery Information Management register/deregister operations on controllers by NQN or device.

Key helpers:
- `nvmf_default_args()` sets defaults such as `tos = -1` and default controller loss timeout.
- `save_discovery_log()` writes raw discovery logs to a user-selected file.
- Hook functions handle retries, connected output, already-connected output, discovery log output, and parsing discovery.conf lines.
- `set_fabrics_options()` maps parsed CLI fields into `libnvmf_context` setters.
- `setup_common_context()` and `create_common_context()` configure endpoint, host identity, queues, reconnect policy, digests, TLS, DHCHAP, duplicate connect, and persistence.
- `create_discovery_context()` adds discovery hooks and discovery-specific defaults.
- `nvme_read_volatile_config()` scans runtime JSON files under the nvme run directory.
- `load_nvme_fabrics_module()` optionally uses libkmod to load `nvme-fabrics`.

Important behavior:
- Uses `libnvme_skip_namespaces()` before topology scans where namespace details are not needed.
- Supports `--config none` to disable JSON config.
- Supports `--dump-config` to write current config to stdout.
- Supports NBFT path selection and `--nbft` / `--no-nbft`.
- Suppresses disconnect errors for missing modules in common unconditional cleanup scenarios.
- Uses global static output/control flags such as `raw`, `persistent`, `quiet`, and `dump_config`.

Integration role:
- Bridges nvme-cli argument parsing and user output with libnvme/libnvmf fabrics APIs.
- Uses `fabrics.h` for declarations and is called by the command dispatch layer.

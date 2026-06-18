# File Research: sources/virtualization/nvme-cli/tests/config.json

Default Python test configuration.

Fields:
- `controller`: `/dev/nvme0`
- `ns1`: `/dev/nvme0n1`
- `log_dir`: `nvmetests`
- `log_level`: `DEBUG`

Role:
- Loaded by `TestNVMe` to select the controller, namespace, log directory, and logging verbosity for hardware-backed tests.

Notes:
- Defaults target real NVMe device nodes and can be destructive for namespace-management tests.

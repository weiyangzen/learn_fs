# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.c

Implements `cloud-SSDplugin-version`.

Behavior:
- Parses no command-specific options.
- Prints hardcoded OCP extension version `1.0`.
- Returns `argconfig_parse()` status.

This is a pure metadata command and does not open an NVMe device.

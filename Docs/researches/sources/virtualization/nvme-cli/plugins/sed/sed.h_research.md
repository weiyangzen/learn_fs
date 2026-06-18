# File Research: sources/virtualization/nvme-cli/plugins/sed/sed.h

SED plugin command registration header. It registers plugin name `sed` with description `SED Opal Command Set`.

Registered commands:
- `discover`
- `initialize`
- `revert`
- `lock`
- `unlock`
- `password`

It includes Linux `sed-opal.h` and uses nvme-cli command-generation macros. `discover` includes an extra `"1"` command metadata argument.

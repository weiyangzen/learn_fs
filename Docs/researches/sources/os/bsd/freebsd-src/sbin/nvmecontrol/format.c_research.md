# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/format.c

Implements `nvmecontrol format` for NVMe Format NVM and secure erase settings.

Key behaviors:
- Supports LBA format, metadata settings, protection information, protection information location, secure erase setting, user-data erase, and cryptographic erase.
- Ensures only one erase mode is selected.
- Resolves namespace device to controller device because Format NVM is an admin command.
- Checks controller support for format and cryptographic erase.
- Enforces controller limitations for per-namespace format/erase.
- Defaults unspecified namespace parameters from current namespace data; global format defaults to zero.
- Sends `NVME_OPC_FORMAT_NVM` passthrough command.

Research notes:
- No interactive confirmation appears in this file, unlike firmware; callers must treat it as destructive.

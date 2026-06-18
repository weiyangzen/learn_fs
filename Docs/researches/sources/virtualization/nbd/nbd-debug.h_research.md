# File Research: sources/virtualization/nbd/nbd-debug.h

Small debug macro header.

It includes `config.h`, defines `DEBUG(...)` as `printf(__VA_ARGS__)` when `DODBG` is enabled and as an empty macro otherwise, and provides a fallback empty `PACKAGE_VERSION`.

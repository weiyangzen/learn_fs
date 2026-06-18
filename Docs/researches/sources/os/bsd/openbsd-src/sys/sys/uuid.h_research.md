# File Research: sources/os/bsd/openbsd-src/sys/sys/uuid.h

Defines DCE-style UUID layout: 32-bit low time, 16-bit mid time, version/time high, clock sequence bytes, and 6-byte node. It also defines internal node and printed-buffer lengths.

Kernel mode exposes `UUID_NODE_LEN`, `UUID_BUF_LEN`, `uuid_snprintf`, and `uuid_printf`; userland typedefs `struct uuid` as `uuid_t`. Useful for filesystem metadata formats that store UUIDs, though this file itself is format-generic.

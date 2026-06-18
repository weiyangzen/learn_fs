# File Research: sources/os/bsd/netbsd-src/sys/sys/uuid.h

Read completely: 82 lines.

Defines DCE-compatible UUID representation and helpers.

Key elements:
- `_UUID_NODE_LEN` is 6 and `_UUID_STR_LEN` is 38.
- `struct uuid` stores DCE UUID fields: time low/mid/high-version, clock sequence, and node bytes.
- Kernel exposes node/string length macros and helpers for printing, big/little-endian encode/decode, and UUID generation.
- Userland typedefs `uuid_t` and exposes `uuidgen()`.

Risks and notes:
- Binary and textual UUID representation must preserve endian conventions.
- Kernel/userland share the same structure layout.

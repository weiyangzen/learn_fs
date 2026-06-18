# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/endian.h

Portability header for endian conversion helpers.

Behavior:
- On Windows, defines `htobe16/32/64`, `htole16/32/64`, and `le16/32/64toh` using `__BYTE_ORDER__` and builtin byte swaps.
- On non-Windows, includes system `<endian.h>`.

Integration:
- Provides consistent endian macros for code that must build on Windows and Unix-like platforms.

Risks:
- Windows branch assumes compiler support for `__BYTE_ORDER__`, `__ORDER_BIG_ENDIAN__`, and `__builtin_bswap*`.
- Big-endian Windows is handled, but likely lightly tested.

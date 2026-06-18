# File Research: sources/os/bsd/freebsd-src/sys/sys/_endian.h

Internal endian helper included only through endian-related public headers.

Key elements:
- Maps compiler byte-order constants to BSD names.
- Defines quad high/low word ordering.
- Exposes POSIX/BSD `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, and `BYTE_ORDER` under visibility rules.
- Provides byte-swap, network-order, and host/endian conversion macros.

Dependencies:
- Requires `sys/cdefs.h`.
- Depends on integer typedefs such as `uint16_t` and `__uint32_t` from surrounding include context.

Research notes:
- Uses compiler builtins for byte swaps.
- Important for filesystem and disk formats that need stable little/big-endian conversions.

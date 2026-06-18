# File Research: sources/local-fs/udftools/include/bswap.h

Endian conversion helper header.

Provides:
- Constant byte-swap macros for 16/32/64-bit values.
- Inline byte-swap functions for 16/32/64-bit values.
- Pointer-based byte-swap macros/functions.
- `le*_to_cpu`, `be*_to_cpu`, `cpu_to_le*`, and `cpu_to_be*` families.
- Constant and pointer variants of those conversions.

Behavior is controlled by `WORDS_BIGENDIAN` from `config.h`:
- On big-endian hosts, little-endian conversions swap and big-endian conversions are identity.
- On little-endian hosts, little-endian conversions are identity and big-endian conversions swap.

Key role: keeps on-disk UDF/ECMA little-endian structures portable across host architectures.

Notable detail: pointer helpers cast directly to integer pointers, so callers must be aware of alignment/aliasing constraints.

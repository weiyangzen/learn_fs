# File Research: sources/virtualization/libblockdev/src/utils/sizes.h

Public convenience header defining binary and decimal byte-size suffix macros for readable storage constants.

Key responsibilities:
- Defines binary suffixes `KIBIBYTE` through `EXBIBYTE` as chained `*1024ULL` macro fragments.
- Provides short IEC aliases `KiB`, `MiB`, `GiB`, `TiB`, `PiB`, and `EiB`.
- Defines decimal suffixes `KILOBYTE` through `EXABYTE` as chained `*1000ULL` macro fragments.
- Provides short SI aliases `KB`, `MB`, `GB`, `TB`, `PB`, and `EB`.

Dependencies and integration:
- Includes GLib, though this header only defines macros and does not use GLib types directly.
- Installed as a public header by `src/utils/Makefile.am` and included by the umbrella `src/utils/utils.h`.
- Used throughout libblockdev plugins to keep storage constants readable, for example filesystem feature limits in `src/plugins/fs/generic.c`, LVM limits in `src/plugins/lvm/lvm-common.c`, and MD RAID defaults in `src/plugins/mdraid.h`.
- Size symbols are included in `docs/libblockdev-sections.txt`, so they are part of the public documentation surface.

Implementation notes:
- The macros are intended to be used as suffix-like fragments, for example `(4 MiB)` expands to `(4 *1024ULL *1024ULL)`.
- The chained definitions make every expanded result an unsigned long long expression, which is useful for large storage constants up to EiB/EB scale.

Notable risks:
- These are not function-like or parenthesized value macros; using them without a left-hand numeric operand is invalid, and using them inside more complex macro expressions requires normal C precedence care.
- Short names such as `KB`, `MB`, and `GB` are broad public macros and can collide with other headers or application code.

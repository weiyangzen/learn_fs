# sources/test-tools/strace/src/linux/32/ioctls_inc.h

Purpose: selects the correct generated 32-bit ioctl table include based on architecture alignment rules.

Important APIs/types/functions: preprocessor branches for `M68K`, `X86_64`, `X32`, `SIZEOF_STRUCT_I64_I32`, and includes `ioctls_inc_align16.h`, `ioctls_inc_align32.h`, or `ioctls_inc_align64.h`.

Control flow: M68K uses 16-bit alignment table; x86_64/x32 and architectures where `struct { i64; i32; }` is smaller than two long longs use 32-bit alignment; all others use 64-bit alignment.

State and persistence behavior: no runtime state; compile-time include selection only.

Dependencies and integration points: consumed by ioctl decoding table generation for 32-bit personalities. Depends on configure-probed structure size macros and architecture defines.

Risks: wrong alignment table maps ioctl numbers to wrong symbolic commands. The size heuristic must match kernel UAPI packing for each supported architecture.

Test signals: build ioctl tables for m68k, x86_64 compat/x32, and an align64 32-bit target; verify known ioctl numbers resolve to expected names in each configuration.

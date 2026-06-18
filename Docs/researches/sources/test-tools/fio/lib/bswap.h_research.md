# sources/test-tools/fio/lib/bswap.h

Purpose: provides big-endian-to-CPU conversion helpers for 32-bit and 64-bit integers.

Important APIs/functions: inline `__be32_to_cpu` and `__be64_to_cpu`. On little-endian builds they manually rearrange bytes; on other builds they return the input unchanged.

Control flow/state: no state. The helpers are pure integer transformations selected at compile time by `CONFIG_LITTLE_ENDIAN`.

Dependencies/integration: includes `inttypes.h` and relies on fio configure endianness macros. It is used where fio reads serialized big-endian values.

Risks/test signals: correctness depends on build-time endian macros matching runtime architecture, which `libfio.c` also checks during initialization. Tests should use known constants such as `0x01020304` and cross-check both endian build paths.

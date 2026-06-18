# sources/user-network-fs/nfs-ganesha/src/include/gsh_intrinsic.h

Purpose: This small portability header centralizes compiler branch prediction hints and cache-line padding constants.

Important APIs/types/functions: `likely(x)` and `unlikely(x)` expand to GCC/GLIBC `__builtin_expect` when available and to plain expressions otherwise. `GSH_CACHE_LINE_SIZE` is 128 on PPC64 and 64 elsewhere. `GSH_CACHE_PAD(_n)` declares a named padding byte array.

Control flow: Runtime code uses the macros in hot paths to hint common branches and to separate frequently written fields across cache lines.

State and persistence: No state is stored. Padding affects in-memory struct layout and false-sharing behavior.

Dependencies and integration points: It relies only on preprocessor/compiler definitions and is safe as a low-level include for infrastructure headers.

Risks: Padding changes ABI/layout when embedded in public structs. Branch hints can make code less readable and, if overused or wrong, can modestly hurt performance. Non-GCC compilers fall back to no-op behavior.

Test signals: Compile on GLIBC and non-GLIBC targets, inspect struct sizes where padding is used, and benchmark hot paths only if changing likely/unlikely placement.

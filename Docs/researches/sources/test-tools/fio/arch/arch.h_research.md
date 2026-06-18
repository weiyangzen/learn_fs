# `sources/test-tools/fio/arch/arch.h`

Purpose: Central architecture abstraction dispatcher for fio.

Important APIs and types: Defines architecture enum values, generic `ARCH_FLAG_*` bits, external `arch_flags`, default `ARCH_CPU_CLOCK_WRAPS`, C/C++ atomic wrapper macros for add/sub/load/store with relaxed/acquire/release orderings, preprocessor selection of the target `arch-*.h`, fallback `tsc_barrier()` under `CONFIG_SYNC_SYNC`, default `arch_init()`, fallback io_uring syscall numbers, and `ARCH_HAVE_IOURING`.

Control flow: Included by platform-independent fio code. The preprocessor selects exactly one architecture header based on compiler macros, then generic code uses feature macros advertised by that header. If no arch header provides `ARCH_HAVE_INIT`, a no-op init is defined.

State and persistence: Declares but does not define `arch_flags`. Atomic wrappers operate on caller-owned state. Arch init may mutate globals depending on selected header.

Dependencies and integration: Depends on C11 `<stdatomic.h>` or C++ `<atomic>`, fio `lib/types.h`, `lib/ffz.h`, and every architecture-specific header.

Risks and test signals: Header selection order matters; `__sparc__` before `__sparc64__` may shadow SPARC64. The C atomic macros cast arbitrary pointers to `_Atomic typeof`, which is practical but relies on compiler extensions. Default io_uring syscall numbers are Linux-specific and overridden only for Alpha. Tests should run preprocessor/compile checks across all supported architectures and validate atomics under C and C++ compilers.

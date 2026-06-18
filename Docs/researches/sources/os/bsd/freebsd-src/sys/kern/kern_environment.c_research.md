# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_environment.c

Read completely: 1162 lines.

## Purpose
Implements the kernel environment system: early static/loader environment ingestion, dynamic kernel environment storage, `kenv(2)`, kernel getenv/setenv APIs, tunable fetch helpers, and typed parsers.

## Main Elements
- Tracks early loader/MD environment in `md_envp` and config-generated static environment in `kern_envp`.
- Initializes static environment policy in `init_static_kenv()`, including `loader_env.disabled`, `static_env.disabled`, and `static_hints.disabled`.
- Converts early environments into dynamic `kenvp` storage in `init_dynamic_kenv()`, with duplicate variable suffixing and sanitization unless early preservation is enabled.
- Implements `sys_kenv()` for dump, loader/static dump, get, set, and unset operations with privilege and MAC checks.
- Provides `kern_getenv()`, `freeenv()`, `testenv()`, `kern_setenv()`, and `kern_unsetenv()`.
- Uses `kenv_lock` and `kenv_acquire()` / `kenv_release()` for safe in-place reads of dynamic variables.
- Parses strings, integer arrays, signed/unsigned integers, quads, booleans, and size suffixes through `getenv_string()`, `getenv_array()`, `getenv_quad()`, `getenv_bool()`, and typed wrappers.
- Exposes `getenv_is_true()` and `getenv_is_false()`.
- Implements `tunable_*_init()` helpers for SYSINIT-driven tunable fetches.

## Dependencies And Integration
Integrated with boot loader/environment handoff, config static environment/hints, SYSINIT ordering, UMA, MAC framework checks, privilege checks, eventhandlers for set/unset, and kernel tunable macros.

## Risk Notes
Early static environment pointers may be invalid across MD relocation, so initialization order matters. Dynamic environment capacity and per-value length are bounded. Duplicate handling mutates early strings temporarily and may sanitize source buffers.

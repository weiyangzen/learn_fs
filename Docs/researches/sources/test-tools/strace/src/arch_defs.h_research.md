# sources/test-tools/strace/src/arch_defs.h

Purpose: central fallback header for architecture-specific build-time capability macros.

Important APIs/types/functions: includes generated `arch_defs_.h` and defines defaults for `HAVE_ARCH_GETRVAL2`, old syscall families, UID16 support, personality counts/names/designators, dedicated error registers, compat capability, syscall-tampering needs, word sizes, time32/time64 availability, and timespec32 availability.

Control flow: preprocessor-only fallback chain: if an architecture file does not define a macro, this header supplies a conservative default derived from `SUPPORTED_PERSONALITIES`, `SIZEOF_LONG`, `SIZEOF_KERNEL_LONG_T`, or `__WORDSIZE`.

State and persistence behavior: no runtime state; affects conditional compilation throughout strace.

Dependencies and integration points: included by core definitions and decoders to select architecture behavior. Generated `arch_defs_.h` is supplied per build/architecture.

Risks: incorrect defaults can silently include/exclude syscall decoders or ABI handling. Personality macros must match arrays and syscall table counts elsewhere.

Test signals: cross-architecture builds, `strace -V` mpers/personality output, and time32/time64 syscall tests validate these fallbacks.

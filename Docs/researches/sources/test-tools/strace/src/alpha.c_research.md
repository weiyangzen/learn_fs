# sources/test-tools/strace/src/alpha.c

Purpose: Alpha-architecture-specific syscall decoders for dual-return-value identity syscalls and OSF statfs variants.

Important APIs/types/functions: guarded by `#ifdef ALPHA`; `decode_getxxid`, `SYS_FUNC(getxpid)`, `SYS_FUNC(getxuid)`, `SYS_FUNC(getxgid)`, `SYS_FUNC(osf_statfs)`, `SYS_FUNC(osf_fstatfs)`, `getrval2`, `tcp->auxstr`, and `xsprintf`.

Control flow: `decode_getxxid` runs only on syscall exit, retrieves the second return value, formats it as aux string with labels `ppid`, `euid`, or `egid`, and returns `RVAL_STR`. OSF statfs decoders print pathname/fd, buffer address, and size.

State and persistence behavior: uses a static buffer for aux output, overwritten on each call. No durable state.

Dependencies and integration points: compiled only for Alpha builds; depends on architecture support for `getrval2` and strace return-value formatting.

Risks: static aux buffer is shared within the tracer process but used synchronously for output. Non-Alpha builds compile none of this code, so coverage depends on architecture CI or cross builds.

Test signals: Alpha-specific syscall tests should verify second return value annotations and OSF statfs argument formatting.

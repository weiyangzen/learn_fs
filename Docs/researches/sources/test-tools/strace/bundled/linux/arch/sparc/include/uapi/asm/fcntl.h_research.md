<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/sparc/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/sparc/include/uapi/asm/fcntl.h

Purpose: SPARC UAPI fcntl header defining SPARC-specific open flags, nonblocking aliases, lock commands, and flock padding.

Important declarations: defines hex values for append, async, create/truncate/exclusive, dsync, nonblock, conditional `O_NDELAY`, noctty, largefile, direct, noatime, cloexec, sync/path/tmpfile, owner commands, lock commands, POSIX lock values, and `__ARCH_FLOCK_PAD`/`__ARCH_FLOCK64_PAD`. Includes generic fcntl.

Control flow: preprocessor conditional distinguishes 64-bit SPARC from other SPARC for `O_NDELAY`.

State and persistence: compile-time constants and struct padding macros.

Dependencies and integration: used by strace for SPARC and SPARC64 decoding.

Risks: native/compat conditional handling can alter values. Flock padding affects structure decoding. Test signals: generated xlat and struct layout tests for sparc/sparc64 personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/sparc/include/uapi/asm/fcntl.h -->

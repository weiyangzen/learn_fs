<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/fcntl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/fcntl.h

Purpose: generic Linux UAPI definitions for open flags, fcntl commands, flock constants, owner structures, and fallback flock layouts.

Important APIs/types: defines `O_ACCMODE`, access modes, open flags under `#ifndef` guards, `O_SYNC` composition, `O_TMPFILE`, fcntl command numbers (`F_DUPFD`, `F_GETFD`, `F_SETFL`, lock commands, OFD locks), owner types and `struct f_owner_ex`, `FD_CLOEXEC`, lock/flock flags, `F_LINUX_SPECIFIC_BASE`, and fallback `struct flock`/`struct flock64`.

Control flow: preprocessor fallback design lets architecture headers override values before including this file. 64-bit lock commands are conditional on `__BITS_PER_LONG == 32 || defined(__KERNEL__)`.

State and persistence: compile-time ABI definitions only.

Dependencies and integration: includes `<linux/types.h>` and is the base for most architecture fcntl headers bundled by strace.

Risks: because many definitions are guarded, include order is semantically important. Struct layout depends on architecture padding macros. Test signals: compile/header extraction tests should validate generic and architecture-overridden constants separately.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/fcntl.h -->

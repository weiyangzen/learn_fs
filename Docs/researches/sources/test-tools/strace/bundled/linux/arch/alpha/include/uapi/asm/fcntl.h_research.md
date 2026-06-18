<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/alpha/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/alpha/include/uapi/asm/fcntl.h

Purpose: Alpha architecture UAPI fcntl/open flag definitions bundled for strace decoding.

Important APIs/types: defines Alpha-specific octal values for `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_NONBLOCK`, `O_APPEND`, `O_DSYNC`, directory/no-follow/largefile/direct/noatime/cloexec/path/tmpfile flags, `__O_SYNC`/`O_SYNC`, lock commands, owner/signal commands, POSIX lock values, and old BSD flock values, then includes `asm-generic/fcntl.h`.

Control flow: preprocessor include guard and macro definitions only. Generic header fills in missing common definitions.

State and persistence: compile-time constants and struct layouts only.

Dependencies and integration: consumed by strace bundled header extraction/build logic to decode Alpha syscall flags correctly.

Risks: architecture-specific numeric values differ substantially from generic Linux; stale values lead to wrong flag names in strace output. Test signals: compare generated xlat values against upstream Linux Alpha UAPI and strace open/fcntl decoder tests for Alpha personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/alpha/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/parisc/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/parisc/include/uapi/asm/fcntl.h

Purpose: PA-RISC UAPI fcntl header with architecture-specific open flag and lock command numbering.

Important declarations: defines octal values for append/create/exclusive/largefile/sync/nonblock/noctty/dsync/noatime/cloexec/directory/nofollow/path/tmpfile, 64-bit lock commands, owner/signal commands, and POSIX lock values. Includes `asm-generic/fcntl.h`.

Control flow: include guard and macro definitions only.

State and persistence: compile-time constants.

Dependencies and integration: feeds strace PA-RISC flag decoding and flock command decoding.

Risks: PA-RISC numbering differs sharply from generic values; stale bundled constants would make decoder output misleading. Test signals: architecture xlat comparison against upstream Linux and strace fcntl tests on PA-RISC or emulated headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/parisc/include/uapi/asm/fcntl.h -->

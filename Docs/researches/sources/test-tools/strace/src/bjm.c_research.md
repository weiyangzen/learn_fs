# sources/test-tools/strace/src/bjm.c

Purpose: decoders for module-management syscalls: `delete_module`, `init_module`, and `finit_module`.

Important APIs/types/functions: `SYS_FUNC(delete_module)`, `SYS_FUNC(init_module)`, `SYS_FUNC(finit_module)`, `printstr`, `printaddr`, `printfd`, `printflags`, and xlat tables `delete_module_flags` and `module_init_flags`.

Control flow: `delete_module` prints module name and flags. `init_module` prints raw module image address, length, and parameter string. `finit_module` prints fd, parameter string, and module init flags.

State and persistence behavior: no persistent state. Reads string arguments from tracee memory; module image bytes are intentionally not dumped.

Dependencies and integration points: uses kernel fcntl/header constants and xlat-generated flag tables. Syscall table entries map module syscalls here.

Risks: parameter strings can be inaccessible or truncated by global string limits. Flag tables must track kernel module option additions.

Test signals: module syscall decoder tests should verify flag names, fd formatting, string handling, and raw module image address output.

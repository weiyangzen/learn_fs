# sources/security-integrity/selinux/libselinux/src/check_context.c

Purpose: Validates whether a context is accepted by the current kernel SELinux policy through `selinuxfs/context`.

Important APIs/types/functions: `security_check_context_raw()` writes a raw context to `selinux_mnt/context`. `security_check_context()` converts translated input to raw before validation.

Control flow: raw validation requires `selinux_mnt`, opens `/context` read-write, writes the NUL-terminated context, closes the descriptor, and returns success if the write succeeded. The translated wrapper handles conversion and freeing.

State and persistence: no persistent state is changed; the kernel validates input against loaded policy.

Dependencies and integration: used as the default validation callback for label lookups and context-list filtering.

Risks and test signals: write length includes the terminating NUL. Tests should cover missing mount, invalid contexts, conversion failure, and descriptor close on write failure.

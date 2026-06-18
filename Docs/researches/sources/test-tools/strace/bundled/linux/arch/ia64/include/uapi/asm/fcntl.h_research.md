<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/ia64/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/ia64/include/uapi/asm/fcntl.h

Purpose: IA64 UAPI fcntl wrapper with architecture-specific large-file behavior.

Important declarations: defines `force_o_largefile()` in terms of `personality(current->personality) != PER_LINUX32`, includes `<linux/personality.h>`, then includes `asm-generic/fcntl.h`.

Control flow: macro and includes only.

State and persistence: compile-time macro behavior; no runtime state in this header.

Dependencies and integration: relevant to kernel-side UAPI snapshots and strace's awareness of IA64 open flag behavior.

Risks: `current` and `personality` are kernel-context concepts, unusual in a UAPI-looking header; consumers must not evaluate it in userspace builds where unavailable. Test signals: ensure bundled processing tolerates the macro and IA64 constants match upstream.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/ia64/include/uapi/asm/fcntl.h -->

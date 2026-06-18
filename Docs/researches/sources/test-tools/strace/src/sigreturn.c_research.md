# sources/test-tools/strace/src/sigreturn.c

Purpose: delegates `sigreturn` decoding to the architecture-specific implementation while providing shared signal-mask print helpers.

Important APIs/types/functions: `print_sigmask_addr_size`, `tprintsigmask_addr`, `arch_sigreturn`, and `SYS_FUNC(sigreturn)`.

Control flow: includes `arch_sigreturn.c`, calls `arch_sigreturn(tcp)`, and returns decoded. The local helper prints a `{mask=...}` wrapper for arch files that expose saved masks.

State and persistence behavior: no persistent local state; architecture code may read registers or tracee signal frames.

Dependencies and integration points: depends on `ptrace.h`, `regs.h`, `nsig.h`, optional `<asm/sigcontext.h>`, and architecture-specific include selection.

Risks: all meaningful ABI risk sits in per-arch `arch_sigreturn.c` files. This wrapper must keep helper names and include order compatible with those files.

Test signals: architecture-specific sigreturn tests should verify decoded frame fields and masks where supported; builds should cover arches with and without asm sigcontext headers.

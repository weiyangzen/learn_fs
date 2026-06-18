# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prsystm.h

## Role

`prsystm.h` is a kernel-only procfs integration header. It declares the procfs-side routines used by the core kernel and other modules to expose process, LWP, register, credential, privilege, secflags, address-space, file-descriptor, watchpoint, stepping, and lifecycle state.

## Key Interfaces

The header exports procfs globals `pr_pidlock` and `pr_pid_cv`, then forward-declares procfs-visible structs such as `pstatus`, `lwpstatus`, `psinfo`, `lwpsinfo`, `prcred`, `prpriv`, `prsecflags`, `prfdinfo`, and register-set types.

Important function groups:
- Status and identity collection: `prgetstatus()`, `prgetlwpstatus()`, `prgetpsinfo()`, `prgetlwpsinfo()`.
- Register access: `prgetprfpregs()`, `prgetprxregs()`, `prgetprxregsize()`, plus SPARC/x86 platform-specific routines.
- Credentials/security: `prgetcred()`, `prgetpriv()`, `prgetsecflags()`.
- Lifecycle hooks: `prexit()`, `prfree()`, `prlwpexit()`, `prlwpfree()`, `prexecstart()`, `prexecend()`, `prrelvm()`.
- Debugging and stopping: `prstop()`, `prunstop()`, `prstep()`, `prnostep()`, `prdostep()`, `prundostep()`, `pr_allstopped()`.
- Address-space/watchpoint helpers: `pr_getprot()`, `pr_getsegsize()`, `prnsegs()`, `prmapin()`, `prmapout()`, `pr_watch_emul()`, `pr_free_watched_pages()`.

## Compatibility Notes

Under `_SYSCALL32_IMPL`, the file declares 32-bit procfs status/register conversion and fetch routines. SPARC exposes register-window helpers and optional ASR access; x86 exposes LDT helpers.

## Research Notes

This is not a public user ABI header. It is the contract between procfs implementation code and kernel process/thread/address-space machinery. Audit changes here with procfs lifecycle, ptrace-like stop/step semantics, zone-aware status reporting, and 32-bit procfs ABI conversion in mind.

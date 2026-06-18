# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_proc.c

Implements process, LWP, argv, and environment retrieval for `libkvm`. It serves both live/sysctl kernels and dead crash dumps.

Key behavior:
- Dead-kernel process listing resolves `_nprocs`, `_allproc`, and `_zombproc`, walks kernel process lists, reads credentials, process groups, sessions, ttys, VM space, and representative LWP wait messages.
- Live process/LWP listing uses `KERN_PROC`, `KERN_PROC2`, and `KERN_LWP` sysctls.
- `kvm_getproc2()` can synthesize `kinfo_proc2` from old `kinfo_proc` plus representative LWP data for dead kernels.
- `kvm_getlwps()` reads LWP sysctl data live or walks a process LWP list in a dump.
- Argument/environment retrieval for old `kinfo_proc` reads `ps_strings` and user pages from the target process VM map or swap; `kvm_getargv2/getenvv2()` use `KERN_PROC_ARGS` sysctl.
- `_kvm_ureadm()` traverses VM map entries, amaps, anon slots, resident pages, or swap slots to read user-space pages from a dump.

Notable risks:
- The file embeds a private copy of kernel credential layout; kernel credential structure drift can break dump interpretation.
- Dead-kernel argv/env extraction depends on VM internals and swap availability.
- Some synthesized `kinfo_proc2` fields are explicitly zeroed or marked `XXX`, so dead-kernel output is best-effort.

## sources/test-tools/syzkaller/sys/linux/init.go

Purpose: Linux target initialization, special type wiring, special pointer/file-length configuration, and neutralization of dangerous or nondeterministic syscalls.

Important APIs/types/functions: `InitTarget`, `arch`, `arch.neutralize`, `neutralizeSchedAttr`, `enforceIntArg`, `neutralizeIoctl`, and `generateTimespec`.

Control flow: `InitTarget` loads many Linux constants, configures POSIX data mmap, assigns neutralization, registers Linux special generators for timespec, AF_ALG, netfilter, USB, and audio descriptors, sets auxiliary resources, architecture-specific special pointers, and special filename lengths. `neutralize` first applies generic Unix neutralization, then rewrites call arguments for mremap, syslog, ioctl, fanotify, ptrace, arch_prctl, init_module, syz_init_net_socket, syz_open_dev, sched_setattr, and ebtables.

State and persistence: mutates in-memory target hooks and per-call arguments during sanitization. No persistence.

Dependencies/integration: depends on generated Linux constants, `targets.MakeUnixNeutralizer`, `targets.MakePosixMmap`, `prog.Gen`, and additional Linux init files for AF_ALG/netfilter/USB generation.

Risks: neutralization protects host stability; missing constants or incomplete rewrites can cause hangs, machine freezes, or nondeterminism. Structural fixes are only partially honored by current target sanitize behavior.

Test signals: `prog_test.go` sanitization/idempotence, all-target generation, and special-struct tests indirectly exercise this logic.

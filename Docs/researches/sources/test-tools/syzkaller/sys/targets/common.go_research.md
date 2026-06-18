# sources/test-tools/syzkaller/sys/targets/common.go

Purpose: shared target helper functions for mmap setup and Unix syscall neutralization.

Important APIs/types/functions: `MakePosixMmap`, `MakeSyzMmap`, `UnixNeutralizer`, `MakeUnixNeutralizer`, and `UnixNeutralizer.Neutralize`.

Control flow: mmap helpers return closures that synthesize initial mapping calls for target data memory. `Neutralize` switches over `mmap`, `mknod/mknodat/compat_50_mknod`, and `exit/exit_group`, adding `MAP_FIXED`, converting dangerous device node modes to regular files except safe loop/null cases, truncating device values, and avoiding executor-reserved exit status.

State and persistence: no durable state; closures capture target constants and mutate in-memory programs.

Dependencies and integration points: used by NetBSD, OpenBSD, and other Unix-like target initializers. Relies on `prog` argument constructors and target constants.

Risks: syscall argument positions are ABI-sensitive. The device-node policy is conservative but may still allow OS-specific unsafe devices unless target-specific neutralizers add more rules.

Test signals: NetBSD/OpenBSD tests exercise parts of this file indirectly.

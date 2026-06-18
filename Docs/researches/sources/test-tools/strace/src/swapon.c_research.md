# sources/test-tools/strace/src/swapon.c

Purpose: decoder for `swapon`.

Important APIs/types/functions: `SYS_FUNC(swapon)`, `SWAP_FLAG_PRIO_MASK`, `swap_flags`, `printpath`, and flag-printing helpers.

Control flow: prints `path`, splits priority bits out of `swapflags`, prints named swap flags if present, then prints the priority numeric component inside the flag expression.

State and persistence behavior: no persistent state; reads only syscall arguments and tracee path memory through `printpath`.

Dependencies and integration points: syscall table maps `swapon` here; depends on `<sys/swap.h>` and generated xlat `swap_flags`.

Risks: priority is always printed even when no explicit priority flag is set, matching the bit-mask representation but potentially surprising for humans.

Test signals: paths valid/invalid, no flags, priority-only, named flags plus priority, and unknown flag bits.

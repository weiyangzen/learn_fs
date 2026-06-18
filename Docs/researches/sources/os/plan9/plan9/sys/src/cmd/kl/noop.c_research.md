# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/noop.c

Read fully: 650 lines, 11140 bytes. SHA-256 prefix: `2a573be829dbf241`.

This file performs major late IR cleanup and expansion before scheduling. `noops()` identifies leaf functions, computes frame and `BECOME` sizes, removes `ANOP`, marks labels/branches/synchronization points, expands prologues/epilogues, lowers `RETURN` and `BECOME`, optionally expands integer multiply/divide/modulo into calls to runtime helper symbols, and finally schedules bounded basic blocks with `sched()`.

Important behavior:
- Marks text symbols as `SLEAF` where no call/prologue save is needed.
- Inserts stack adjustment and saved link register stores for non-leaf functions.
- Converts returns into `AJMP` through link registers or restores link from stack.
- Tracks maximum `BECOME` space and defines `ALEFbecome`.
- Uses `initmuldiv()` to locate `_mul`, `_div`, `_divl`, `_mod`, `_modl`.
- Splits scheduling regions at labels, branches, sync instructions, NOSCHED spans, and `NSCHED` size.

Risk notes: transformation order matters. `ANOP` stripping assumes `q` is a preceding non-nop. Helper expansion mutates the original arithmetic instruction into stack adjustment and inserts a call sequence after it.

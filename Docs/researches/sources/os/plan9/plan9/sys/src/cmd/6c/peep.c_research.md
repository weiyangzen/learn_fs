# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/peep.c

This file performs amd64 peephole optimizations over the register-flow graph built by `reg.c`. It first ensures the `Reg` graph has a node for every executable instruction, then repeatedly applies local copy and instruction simplifications.

Main optimizations include copy propagation for register-to-register moves, substitution propagation to expose removable moves, collapse of repeated sign/zero extension moves, and conversion of add/sub by one into inc/dec when flags are not needed. `needc` prevents transformations that would break carry-dependent instructions.

The copy analysis classifies instruction use of operands with `copyu`: read-only, set-only, read-alter-write, use-and-set, or untouched. It handles special amd64 constraints for `AX`/`DX` division, `CX` shifts/repeats, string instructions, calls, returns, and branch targets.

`excise` turns eliminated instructions into `NOP`, later removed by register optimization cleanup.

Filesystem relevance is compiled-code quality. Kernel/filesystem routines can be sensitive to instruction count, and these simple backend optimizations reduce redundant moves without changing source code.

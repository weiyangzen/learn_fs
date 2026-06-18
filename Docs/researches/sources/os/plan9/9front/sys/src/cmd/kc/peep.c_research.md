# File Research: sources/os/plan9/9front/sys/src/cmd/kc/peep.c

Peephole and copy-propagation optimizer over the register flow graph produced by `reg.c`. It first fills gaps in the `Reg` graph for non-data pseudo instructions, then repeatedly removes redundant register moves via `copyprop` and `subprop`. It also eliminates repeated sign/zero extension moves such as `MOVB x,R; MOVB R,R`.

The optimizer classifies instruction register effects with `copyu`: read, write, read-alter-write, or untouched. Helper functions detect direct and indirect register use (`copyas`, `copyau`, `copyau1`) and substitute registers in operands. It is conservative around jumps, calls, returns, and unknown opcodes.

# File Research: sources/os/plan9/9front/sys/src/cmd/kl/noop.c

Linker pass for pseudo-op cleanup, frame/prologue/epilogue synthesis, branch labeling, multiply/divide helper expansion, and instruction scheduling boundaries. `noops` first strips nops, marks labels/sync points/branches/floating ops, detects leaf functions, records frame and “become” sizes, and marks branch targets.

It then adjusts caller frames for `BECOME`, inserts stack adjustment and saved-link prologue code, expands returns differently for leaf and non-leaf functions, rewrites integer mul/div/mod into calls to `_mul`, `_div`, `_divl`, `_mod`, or `_modl` when hardware/debug settings require it, and invokes `sched` on bounded basic blocks. `addnop` and `initmuldiv` support those transformations.

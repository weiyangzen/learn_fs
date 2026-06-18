# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/noop.c

Instruction cleanup, frame/prologue/epilogue generation, leaf detection, and optional scheduling entry point.

Main flow in `noops()`:
- Scans the instruction list to identify leaf functions, frame sizes, branch labels, floating-point operations, synchronization-sensitive instructions, and call/become requirements.
- Removes `ANOP` nodes by relinking them out while preserving marks.
- Tracks maximum `BECOME` stack requirement and defines `ALEFbecome`.
- Adjusts calling function frame sizes when calls may need extra become space.
- Expands `ATEXT` into function prologue code:
  - computes `autosize`;
  - suppresses save/restore for true leaf functions;
  - emits stack adjustment and link-register save using `REGTMP`.
- Expands `ARETURN` into actual return sequences:
  - direct branch to LR for frameless leaf functions;
  - stack restoration for leaf functions with frames;
  - LR restore plus stack adjustment for non-leaf functions;
  - special handling for `BECOME`.
- If debug flag `Q` is enabled, schedules basic blocks by invoking `sched()` around labels, branches, syncs, and `NOSCHED` runs.

`addnop()` inserts a PowerPC no-op as `NOR R0,R0`.

Risk/notes:
- Correctness depends on conservative marks for instructions touching special registers and memory synchronization.
- `NOSCHED` regions are preserved during scheduling.
- Leaf/non-leaf decisions affect ABI-visible stack and LR handling.

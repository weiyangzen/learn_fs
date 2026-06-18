# File Research: sources/os/plan9/9front/sys/src/9/zynq/init9.s

Purpose: Tiny Plan 9 ARM startup adapter that jumps into `startboot`.

Key behavior:
- Sets static base register `R12`.
- Moves boot arguments from stack/registers into expected positions.
- Branches to `startboot`.

Integration notes: This is an early entry shim before the broader Zynq assembly startup in `l.s`.

Risk/attention points: It relies on exact calling/stack convention at kernel entry.

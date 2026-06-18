# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/plan9.c

Provides Plan 9 system bindings and constants for host `sam`.

Key contents:
- Defines `samname`, bracket delimiter tables `left`/`right`, and system command/path constants: `RSAM`, `SAMTERM`, `HOME`, `TMPDIR`, `SH`, `RX`, and `SAMSAVECMD`.
- `dprint`, `print_ss`, and `print_s` route messages through `termwrite`.
- `statfile` and `statfd` wrap Plan 9 `dirstat`/`dirfstat`.
- `notifyf` handles interrupt and closed-pipe notifications.
- `waitfor` filters wait messages by pid and returns exit status text.
- `samerr`, `emalloc`, and `erealloc` centralize temp error naming and allocation failure behavior.

Behavior notes:
- `notifyf` converts interrupts into `intr()` and ignores closed-pipe notes only when `bpipeok` is set.
- Allocation wrappers zero new memory for `emalloc` and panic on failure.

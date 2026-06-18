# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termio.h

## Purpose
Provides the legacy System V `termio` interface layered on top of `termios.h`.

## Main Interfaces
- `struct termio`: 16-bit input/output/control/local flags, line discipline, and `_NCC` control characters.
- `IOCTYPE`, `TCDSET`, and optional `TTYTYPE`.
- `struct termcb`: legacy line-discipline terminal control block.
- Default speed `SSPEED`.
- Terminal type constants such as `TERM_NONE`, `TERM_TEC`, `TERM_V61`, `TERM_V10`, and others.
- Terminal flag constants:
  - `TM_NONE`
  - `TM_SNL`
  - `TM_ANL`
  - `TM_LCF`
  - `TM_CECHO`
  - `TM_CINVIS`
  - `TM_SET`

## Dependencies And Relationships
Includes `sys/termios.h`, which supplies most ioctl codes and modern flag definitions.

## Research Notes
This is a compatibility header for older APIs. New terminal code generally uses `termios`.

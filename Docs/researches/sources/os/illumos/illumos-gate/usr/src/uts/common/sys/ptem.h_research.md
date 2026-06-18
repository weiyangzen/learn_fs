# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptem.h

## Role

`ptem.h` defines the private state used by the pseudo-terminal emulation STREAMS module.

## Data Model

`struct ptem` stores:
- `cflags`: cached terminal control flags.
- `dack_ptr`: preallocated message block used to ACK disconnects.
- `q_ptr`: the ptem read queue.
- `wsz`: terminal window size.
- `state`: ptem state bits.

The state bits are:
- `REMOTEMODE`: pty remote mode.
- `OFLOW_CTL`: output flow control active.
- `IS_PTSTTY`: X/Open terminal mode.

The header also defines `RDSIDE` and `WRSIDE` constants to distinguish common helper calls from read-side versus write-side put procedures.

## Research Notes

This is a small STREAMS terminal-module state header. The main correctness concerns are stable interpretation of `state` bits and consistent queue/message ownership between ptem read/write-side code.

# File Research: sources/os/bsd/netbsd-src/lib/libedit/sig.h

## Purpose
Private signal subsystem declarations.

## Main Declarations
- `ALLSIGS`: macro list of signals libedit traps while editing.
- `ALLSIGSNO`: count of trapped signals.
- `el_signal_t`: saved `sigaction` array, signal set, and volatile last signal number.
- Lifecycle and control functions: `sig_init`, `sig_end`, `sig_set`, `sig_clr`.

## Integration
`read.c` installs and clears handlers around line reads when `HANDLE_SIGNALS` is enabled. `sig.c` owns the implementation.

## Risks And Notes
The signal list count must match `ALLSIGS`. Adding or removing signals requires updating both the macro list and count.

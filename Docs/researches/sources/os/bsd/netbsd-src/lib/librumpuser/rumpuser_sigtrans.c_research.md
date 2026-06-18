# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sigtrans.c

## Purpose
Translates rump kernel signal numbers to host signal constants.

## Main Interfaces
Exports `rumpuser__sig_rump2host(int)`.

## Control Flow And State
The function is a switch over NetBSD-style signal numbers 0 through 32. Each case is guarded by the corresponding host `SIG*` macro. Signal 20 maps to `SIGCHLD` or `SIGCLD` depending on availability. Unknown or unavailable signals return `-1`.

There is no mutable state.

## Dependencies
Depends on host `<signal.h>` signal macro definitions.

## Risks And Notes
The mapping assumes NetBSD numeric signal assignments on the rump side. Host platforms with missing or differently named signals may return `-1` for otherwise valid rump signals.

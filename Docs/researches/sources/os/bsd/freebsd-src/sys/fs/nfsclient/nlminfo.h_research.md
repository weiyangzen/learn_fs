# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nlminfo.h

## Purpose
Defines `struct nlminfo`, a small per-process/per-locking-context carrier for NLM-based advisory locking state.

## Main Data
- `msg_seq`: sequence counter for lock requests.
- `retcode`: return code from lock requests.
- `set_getlk_pid` and `getlk_pid`: PID bookkeeping for `F_GETLK`-style interactions.
- `pid_start`: process start time used to disambiguate lock ownership across PID reuse.

## Integration
Used by NFS/NLM locking code outside this group and populated through client mount/vnode information for lockd interactions.

## Risks
The structure is simple; correctness depends on external NLM/lockd code updating sequence, return code, and PID identity fields consistently.

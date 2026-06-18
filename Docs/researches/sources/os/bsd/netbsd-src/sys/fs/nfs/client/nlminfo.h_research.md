# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nlminfo.h

## Purpose
Defines `struct nlminfo`, small per-process/per-locking context state used by NLM-based advisory locking.

## Main Data
- `msg_seq`: sequence counter for lock requests.
- `retcode`: return code from lock requests.
- `set_getlk_pid` and `getlk_pid`: PID bookkeeping for `F_GETLK` style interactions.
- `pid_start`: process start time used to disambiguate lock owners across PID reuse.

## Integration
Used by NFS/NLM lock manager code outside this group to preserve state needed by the master lockd process and by processes doing NLM locking.

## Risks
Small state carrier only; correctness depends on external lockd/NLM code updating sequence and PID fields consistently.

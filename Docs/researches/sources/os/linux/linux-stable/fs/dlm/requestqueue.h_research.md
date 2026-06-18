# File Research: sources/os/linux/linux-stable/fs/dlm/requestqueue.h

## Purpose
`requestqueue.h` declares recovery-time request queue helpers.

## Exports
- `dlm_add_requestqueue()`
- `dlm_process_requestqueue()`
- `dlm_wait_requestqueue()`
- `dlm_purge_requestqueue()`

## Notes
`dlm_wait_requestqueue()` is declared here but not defined in the listed source file; it is either defined elsewhere in the DLM tree or a stale declaration.

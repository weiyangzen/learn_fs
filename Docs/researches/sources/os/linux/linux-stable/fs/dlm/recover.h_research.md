# File Research: sources/os/linux/linux-stable/fs/dlm/recover.h

## Purpose
`recover.h` declares recovery helpers used by recoverd, RCOM, lock, and membership code.

## Exports
- Wait/status helpers: `dlm_wait_function()`, `dlm_recover_status()`, `dlm_set_recover_status()`.
- Barrier waits: members, directory, locks, done.
- Master recovery: `dlm_recover_masters()`, `dlm_recover_master_reply()`.
- Lock recovery: `dlm_recover_locks()`, `dlm_recovered_lock()`.
- RSB cleanup/finalization: `dlm_clear_inactive()`, `dlm_recover_rsbs()`.

## Notes
The header exposes only recovery-stage orchestration, not lower-level RSB list internals.

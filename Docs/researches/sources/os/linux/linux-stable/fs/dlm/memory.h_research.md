# File Research: sources/os/linux/linux-stable/fs/dlm/memory.h

## Purpose
`memory.h` declares DLM memory-cache lifecycle and typed object allocation APIs.

## Exports
- Lifecycle: `dlm_memory_init()`, `dlm_memory_exit()`.
- Object allocation/free: RSB, LKB, LVB, mhandle, writequeue entry, lowcomms message, callback.

## Notes
The header hides cache implementation details from the rest of DLM while preserving typed allocation calls.

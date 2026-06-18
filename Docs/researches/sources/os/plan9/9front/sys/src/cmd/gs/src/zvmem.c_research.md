# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem.c

## Purpose
Implements core PostScript virtual-memory operators: `save`, `restore`, `vmstatus`, and Ghostscript extension `.forgetsave`.

## Key Elements
Defines `vm_save_t` to associate allocator save levels with saved graphics state. Public routines include `zsave`, `restore_check_save`, `dorestore`, `zrestore`, and `zvmstatus`.

## Behavior/Risks
`save` allocates a local VM save record, creates allocator save state, and saves graphics state. `restore` validates the save operand, scans operand/exec/dictionary stacks for objects newer than the save, fixes stack refs and executable empty strings/files, then iteratively restores allocator and graphics state. `.forgetsave` removes a save without restoring memory state by splicing graphics-state save chains and forgetting the allocator save. `dorestore` temporarily clears `LockFilePermissions` after restore so restored user parameters can be reapplied without invalid access.

## Dependencies
Uses allocator save internals, stack enumeration, graphics state save/restore, dictionary stack cache reload, file refs, and memory status APIs.

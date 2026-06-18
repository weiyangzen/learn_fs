# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem.c

## Purpose
Implements PostScript save/restore virtual-memory operators and related VM status/forget-save extension.

## Public Surface
- `zsave`, `zrestore`.
- Private operators: `vmstatus`, `.forgetsave`.
- Registered through `zvmem_op_defs`.

## Implementation Notes
- `vm_save_t` stores the graphics-state save boundary associated with a VM save.
- `zsave` optionally validates memory, allocates a local save record, creates allocator save state, performs `gs_gsave_for_save` and `gs_gsave`, and returns a `t_save` ref.
- `zrestore` validates the save object, checks all operand/execution/dictionary stack refs are older than the target save, fixes stack refs, iteratively restores allocator state, restores graphics state at each save level, refreshes dictionary cache, and temporarily clears `LockFilePermissions`.
- `restore_check_stack` rejects stack refs to objects allocated since the save, with special exceptions for executable/closed e-stack files and empty executable strings.
- `restore_fix_stack` clears `l_new` and canonicalizes newer empty executable strings or closed executable files on the e-stack.
- `vmstatus` reports local save level, used VM, and available allocation accounting.
- `.forgetsave` removes a save without restoring VM, while splicing graphics-state save chains and forgetting allocator state.

## Dependencies
Uses allocator save/restore internals, graphics state save/restore, stacks, files/streams, dictionaries, memory validation, and matrix/graphics-state headers.

## Risks and Notes
- Save/restore is memory-ownership-sensitive; invalid stack references must be detected before allocator rollback.
- Graphics-state restoration and VM restoration are coupled through `vm_save_t`.
- `.forgetsave` is non-standard and manipulates graphics-state save chains directly.
- Filesystem relevance: indirect through file refs on the execution stack during restore validation.

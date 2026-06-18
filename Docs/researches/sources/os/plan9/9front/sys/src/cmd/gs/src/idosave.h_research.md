# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idosave.h

Declares low-level save-recording helpers for restore support.

Key points:
- `alloc_save_change` and `alloc_save_change_in` record changes that must be undone by `restore`.
- APIs take the containing object ref and the changed ref/packed-ref pointer.
- Comments explain the container is needed to choose the correct VM saved-change chain and to trace/relocate change records during GC.

Research notes:
- This is foundational for PostScript save/restore semantics over arrays, dictionaries, and structs.

# File Research: sources/os/plan9/9front/sys/src/cmd/sam/file.c

`file.c` layers sam file semantics over `Buffer`: file naming, modification state, undo/redo logs, edit merging, dot/mark state, and terminal rasp synchronization.

Undo records are stored backwards in `delta` and `epsilon` buffers as `Undo` structs, optionally preceded by associated rune data. This allows reversing the most recent grouped edit by reading from the end.

`loginsert` and `logdelete` log edits, merge nearby changes into a `Merge` accumulator, enforce sequence ordering through `hiposn`, and mark files dirty. `flushmerge` emits pending merged insert/delete records.

`logsetname`, `fileunsetname`, `fileunsetdot`, and `fileunsetmark` log metadata changes so file names, dot, and mark participate in undo/redo.

`fileupdate` flushes merged edits, records dot/mark state, runs redo-style application from `epsilon` into the main buffer and rasp, and updates dirty/close state. `fileundo` performs both undo and redo depending on which transcript is treated as source and whether reverse records are emitted.

`fileload`, `filereadc`, `filesetname`, `fileclose`, `filereset`, and `filemark` provide file lifecycle, character access, initial load, and per-command sequence checkpointing.

# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sam.c

`sam.c` is the host editor's main program and high-level file/session coordinator.

`main` parses sam and samterm options, initializes strings, disk storage, terminal connection, notify handling, current directory, initial files, current file, sequence number, and command loop. Downloaded mode starts `samterm` and speaks the sam protocol; non-downloaded mode operates on stdin/stdout.

`rescue` writes dirty buffers to `$home/sam.save` as shell commands that can reconstruct file contents. `panic` and `hiccough` handle fatal/internal and command-level errors, including rollback of edits logged in the current sequence.

File/session operations include dirty-close checking, dirty-quit checking, lazy file load, command-file update, file deletion, per-command update of modified files, and current-file selection.

`edit`, `getname`, `filename`, and `writef` integration handle `e`, `r`, `I`, `f`, and file naming semantics, including clean-sequence management and modified-state updates.

The file-list helpers (`readcmd`, `cd`, `loadflist`, `readflist`, `tofile`, `getfile`, `closefiles`) implement sam's file name/menu command behavior and current-directory normalization.

Text operations include `copy`, `move`, `nlcount`, `printposn`, and `settempfile`, supporting command execution over stable snapshots of the open-file list.

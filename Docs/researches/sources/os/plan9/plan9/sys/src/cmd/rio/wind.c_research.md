# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/wind.c

Read status: complete, 1699 lines.

`wind.c` implements the `Window` object and most per-window behavior. It creates windows, manages frame drawing, text buffers, selections, command editing, raw/hold modes, console read/write coordination, mouse selection, scrolling, resize/move/delete messages, process note delivery, shell startup, double-click matching, and history trimming.

`wmk` constructs a `Window` with channels and frame geometry. `winctl` is the per-window event loop, multiplexing keyboard, mouse, console reads/writes, mouse reads, and `wctl` reads. It buffers console output into the window text, services shell input reads line-by-line or raw, queues mouse events, and reports window geometry/state to `wctl` readers.

Editing support includes filename completion, erase character/word/line handling, interrupt delivery to `/proc/<pid>/notepg`, snarf/cut/paste, plumbing, double-click bracket/quote/word selection, visible-origin tracking, selection repainting, and high-water trimming of window history.

Lifecycle functions include `wresize`, `wclose`, `wclosewin`, `wsetpid`, and `winshell`, which mounts the per-window filesystem before executing a shell.

Filesystem relevance: central. It provides the backing state and synchronization semantics for `rio`’s per-window files.

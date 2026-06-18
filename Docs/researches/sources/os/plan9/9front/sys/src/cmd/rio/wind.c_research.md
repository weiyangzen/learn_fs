# File Research: sources/os/plan9/9front/sys/src/cmd/rio/wind.c

`wind.c` is rio's core per-window implementation. It owns window lookup, z-ordering, current-input transitions, cursor selection, frame resizing/redrawing, text history storage, selections, scrolling, keyboard editing, mouse selection/chording, completion, and shell startup.

The window text model is a rune buffer with visible frame state. `winsert`, `wdelete`, `wfill`, `wsetorigin`, and `wshow` maintain the backing buffer, frame contents, origin, host read point `qh`, and selection positions. History is bounded by `HiWater`/`LoWater`, trimming old text when appending output at the tail.

The control path is centered on `winctl`, a threaded event loop using `Alt` over keyboard, mouse, cons read/write, wctl read, completion, and control-message channels. `wctlmesg` handles resize/repaint/refresh/move/raw/hold/truncate/delete/exit transitions and frees all per-window resources on `Exited`.

Input behavior is split between local rio editing and client-visible device state. Keyboard navigation works when client mouse/kbd devices are not open; raw mode queues runes directly for `/dev/cons`; hold mode suppresses cons reads; delete sends an interrupt note via `/proc/.../notepg`.

Mouse behavior includes selection, double/triple-click expansion over words, whitespace regions, lines, and bracket pairs, scroll bar handling, cut/paste chords, and cursor movement conversion from window to screen coordinates.

Filename completion is asynchronous: `namecomplete` computes a directory/path prefix, starts `completeproc`, and `winctl` consumes `Completion` results by inserting completions or displaying candidates in the window text.

`wmk`, `wresize`, `wsetname`, `wclose`, `wclunk`, and `winshell` connect the graphical window, rio file server mount, reference counting, shell process launch, `/dev/cons` setup, and cleanup.

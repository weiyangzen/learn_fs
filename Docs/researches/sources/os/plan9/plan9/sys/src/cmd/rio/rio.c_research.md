# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/rio.c

Read status: complete, 1191 lines.

This is the main `rio` window manager program. It initializes display, mouse, keyboard, screen, background, timers, global channels, synthetic filesystem service, optional startup command, optional keyboard window, and then waits for exit.

It handles snarf import/export, startup command execution, shutdown notes, killing child process groups, keyboard dispatch, mouse dispatch, screen resize, button menus, sweeping new windows, moving/resizing by drag bands, hiding/unhiding, deleting, and creating windows.

Button 3 drives global window operations; button 2 drives per-window cut/paste/snarf/plumb/send/scroll actions. Mouse handling decides when to send events into a client window versus when to top, move, resize, scroll, or invoke menus.

`new` constructs a `Window`, starts its control thread, optionally starts a shell through `winshell`, and records pid/label/working directory.

Filesystem relevance: orchestrates the `rio` filesystem server and creates the windows whose state is exposed as `/dev` files.

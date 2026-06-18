# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/exporter.c

## Role

`exporter.c` wires the synthetic device table into a mountable 9P service for the VNC server's private namespace.

## Main Behavior

- `mounter()` mounts each exported root onto a target mount point using numeric attach names.
- `exporter()` initializes each requested device, attaches its root channel, creates a pipe, returns both pipe ends, and starts an exporter process.
- `extramp()` runs in a new name group, calls `sysexport()` over the pipe, invokes `shutdown()`, and exits when export ends.

## Notable Limitations And Risk Areas

- `Exporter ex` is stack-allocated in `exporter()` and passed to `kproc()`; this relies on the child using it before the parent stack frame becomes invalid.
- Mounting switches from `MREPL` to `MAFTER` after the first mount to layer multiple roots.
- Export failure eventually triggers global VNC server shutdown.

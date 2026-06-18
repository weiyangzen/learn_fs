# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/exporter.c

Helper for exporting synthetic VNC devices over a local 9P connection and mounting them.

Key responsibilities:
- Initializes each supplied `Dev`, attaches its root channel, and gathers roots.
- Creates a pipe pair for 9P traffic.
- Starts an `exporter` kproc that runs `sysexport()` in a private namespace and calls `shutdown()` on exit.
- Provides `mounter()` to mount each exported root on a target mount point using numeric attach specs.

Important behavior:
- Multiple roots are mounted by duplicating the pipe fd and using attach names `"0"`, `"1"`, etc.
- First mount uses the requested mount flag; subsequent `MREPL` mounts become `MAFTER`.

Risks:
- `exporter()` passes a stack `Exporter` struct to a new process sharing memory; it relies on the child consuming it immediately.
- Errors during device attach are converted to `werrstr`.

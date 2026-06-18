# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/Makefile

Build recipe for drawterm’s user-space kernel facade archive.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libkern.a` from channel, device, process, namespace, queue, draw/input, networking, SSL/TLS, terminal, locking, and OS-specific objects.
- Selects audio and OS-specific device variants using `$(AUDIO)` and `$(OS)`.

Role in this group:
- Defines the kernel compatibility layer linked into drawterm.

Notable risks:
- Object selection is configuration-sensitive; missing `AUDIO` or `OS` variants can break the build.

# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/drawterm.h

Read fully: 13 lines, 472 bytes. SHA-256 prefix: `dca4c99cfd4ee707`.

This small header declares cross-module drawterm entry points and globals.

It exposes secstore/auth helpers, console input, exportfs, user/key lookup helpers, factotum dialing, user lookup, and `cpumain()`.

Integration: included by CPU/auth-related drawterm files to share interfaces without a larger public header.

Risk notes: it is purely declarations and relies on matching definitions across the drawterm portability tree.

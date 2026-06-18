# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/pcwin.mak

Partial Ghostscript makefile for PC window-system-specific device drivers shared by MS Windows and OS/2 builds.

It isolates devices needing special platform compilation switches:

- Deprecated MS Windows 3.x DLL display device objects: `gdevmswn`, `gdevmsxf`, `gdevwdib`, plus color mapping helpers.
- MS Windows DDB and DIB printer device targets: `mswinprn.dev` and `mswinpr2.dev`.
- OS/2 Presentation Manager devices: `os2pm.dev` and `os2dll.dev`.
- OS/2 printer device: `os2prn.dev`.

It defines per-object dependencies and uses `GLCCWIN` or `GLCC` as appropriate.

This is device build wiring for Ghostscript, not runtime filesystem implementation.

# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/pcwin.mak

Makefile fragment for PC window-system-specific Ghostscript devices shared by MS Windows and OS/2 builds. It is separated because Windows code needs special compile switches and include paths.

It defines rules for deprecated MS Windows DLL/display devices, Windows DDB/DIB printer devices, OS/2 Presentation Manager devices, and OS/2 printer devices. Targets assemble `.dev` modules from objects such as `gdevmswn`, `gdevmsxf`, `gdevwdib`, `gdevwprn`, `gdevwpr2`, `gdevpm`, and `gdevos2p`.

Dependencies include Windows headers, OS/2/Windows Ghostscript DLL headers, device memory/color helpers, printer device headers, and make variables from platform makefiles.

Filesystem relevance is indirect and limited to userland printer/display build integration.

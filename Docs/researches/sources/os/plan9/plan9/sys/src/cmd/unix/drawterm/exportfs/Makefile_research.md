# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/Makefile

Read fully: 16 lines, 200 bytes. SHA-256 prefix: `43b63e6454b4980d`.

This makefile builds drawterm’s `libexportfs.a`.

It includes `../Make.config`, sets `LIB=libexportfs.a`, compiles `exportfs.$O` and `exportsrv.$O`, archives them with `$(AR) r`, and runs `$(RANLIB)`. The pattern rule compiles local C files with configured compiler flags.

Integration: invoked by the top-level drawterm makefile’s `exportfs/libexportfs.a` target.

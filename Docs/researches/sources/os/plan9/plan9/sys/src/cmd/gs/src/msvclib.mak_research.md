# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvclib.mak

`msvclib.mak` is an MSVC makefile for building the Ghostscript graphics library/tester rather than the full Windows interpreter application. It shares much of the Windows configuration structure with `msvc32.mak`.

It defines install/runtime paths, debug options, build directories, third-party source locations, MSVC tool locations, environment setup, CPU/FPU selection, synchronization, feature libraries, band-list storage, file implementation, and a minimal default device set. For library mode it forces `STDIO_IMPLEMENTATION` blank, `MAKEDLL=0`, and `PLATFORM=mslib32_`.

The included make fragments are `version.mak`, `msvccmd.mak`, `winlib.mak`, and `msvctail.mak`. It adds a `gp_mslib.obj` platform module and creates `mslib32_.dev` by including `mswin32_.dev`.

The main output target links the `gslib` console tester executable using the generated link trace plus `gsnogc`, `gconfig`, and `gscdefs`. This is specialized build infrastructure for embedding/testing the graphics library, not the normal end-user Windows executable path.

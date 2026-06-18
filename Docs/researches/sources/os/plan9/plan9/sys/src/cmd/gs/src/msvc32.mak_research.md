# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvc32.mak

`msvc32.mak` is the top-level Microsoft Visual C++ makefile for 32-bit Windows Ghostscript, with partial support for 64-bit toolchains. It is designed for `nmake` and makes most configurable options overridable with `!ifndef`.

The options cover build directories, install/runtime paths, debug modes (`DEBUG`, `TDEBUG`, `DEBUGSYM`, `NOPRIVATE`), executable/DLL names, `MAKEDLL`, third-party source locations, IJG/libpng/zlib/JBIG2/Jasper/ICC/IJS settings, large 64-bit `gx_color_index`, warning level, MSVC version detection, Visual Studio/DDK tool paths, include/lib environment setup, CPU/FPU selection, synchronization module, language features, band-list storage, file/stdio implementations, and a large default device set for Windows.

After including `msvccmd.mak`, `winlib.mak`, `msvctail.mak`, and `winint.mak`, it defines the main Windows outputs. In DLL mode it builds small GUI and console loaders plus `gsdll32.dll`; without DLL mode it builds large GUI and console executables. It also links setup and uninstall helpers in DLL mode and provides recursive debug targets.

The file is central Windows build glue. Risks are old MSVC-version assumptions, complex conditional path handling, link response-file generation through shell `echo`, and the need to keep feature/device lists synchronized with the included Ghostscript make fragments.

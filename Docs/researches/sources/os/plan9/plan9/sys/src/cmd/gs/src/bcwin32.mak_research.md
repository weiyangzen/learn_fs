# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/bcwin32.mak

This is the Ghostscript makefile for Win32 builds using Borland C++/C++Builder.

Core responsibilities:
- Defines build directories, install root, runtime library/font search paths, executable names, and DLL/executable build mode.
- Supports Borland C++ 4.5 and C++Builder 3/4/5 path layouts.
- Defines compiler, linker, resource compiler, auxiliary compiler, CPU/FPU flags, multithread flags, debug flags, and DLL/executable calling convention flags.
- Selects Ghostscript features and Windows-oriented devices, including display, Windows DLL, printer, BMP, TIFF, PNG, JPEG, PDF/PS writers, and many legacy printer devices.
- Includes `winlib.mak` and `winint.mak` for the generic Windows library/interpreter build rules.
- Builds auxiliary tools such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.

Output shapes:
- With `MAKEDLL=1`, builds small graphical and console loader executables plus a large `gsdll32.dll`.
- With `MAKEDLL=0`, builds large standalone graphical and console executables.
- May build `gs16spl.exe` for Win32s 16-bit spooler access when supported by the selected Builder version.
- Also contains setup and uninstall executable targets for DLL builds.

Notable quirks:
- The file includes old Borland response-file and linker-script generation patterns.
- It contains comments and conditionals for obsolete Windows environments.
- Filesystem interaction is build/install artifact generation only; it does not implement filesystem behavior.

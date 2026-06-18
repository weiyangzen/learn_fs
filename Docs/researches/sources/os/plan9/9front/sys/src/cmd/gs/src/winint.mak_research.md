# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winint.mak

Common interpreter makefile section for 32-bit Microsoft Windows.

Key points:
- Includes generic interpreter and compiled-font makefiles.
- Defines Windows interpreter compile commands and resource compiler include handling.
- Defines default paths for WinZip self-extractor, zip tool, setup executable, and uninstall executable.
- Builds icon resources from `.icx` files using `echogs`.
- Builds short EXE and DLL resource files by generating temporary `.rc` files.
- Defines Windows object groups for DLL, non-DLL, console, and graphical builds.
- Compiles Windows frontend modules: `dwdll`, `dwnodll`, `dwmain`, `dwmainc`, `dwimg`, `dwtext`, `dwtrace` in debug builds, `dwreg`, setup, install, and uninstall modules.
- Provides `zip` and `archive` targets for AFPL Ghostscript Win32 distribution packaging with setup/uninstall programs and font packaging.

Dependencies and interactions:
- Designed to be acceptable to MSVC, Watcom, and Borland make dialects; only simple conditionals are allowed.
- Included by Windows top-level makefiles such as `watcw32.mak`.
- Relies on `winlib.mak`, `int.mak`, `cfonts.mak`, resource files, and generated Ghostscript version variables.

Research relevance:
- Defines the Windows interpreter frontend, resources, installer tooling, and distribution archive generation.

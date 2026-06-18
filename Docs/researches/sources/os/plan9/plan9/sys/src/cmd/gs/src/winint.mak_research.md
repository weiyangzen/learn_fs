# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winint.mak

Common interpreter makefile section for 32-bit Windows.

Key points:
- Includes `int.mak` and `cfonts.mak`.
- Defines Windows interpreter compile macros and `GLCPP`.
- Sets paths for WinZip self-extractor, zip tool, setup, and uninstall executables.
- Builds icon resources from `.icx` text form using `echogs`.
- Builds resource files for small EXE loader and DLL/main program.
- Defines object sets for big EXE, console EXE, small EXE loader, and DLL modes.
- Compiles Windows interpreter modules such as `dwnodll`, `gsdll`, `gp_msdll`, `dwmainc`, `dwdllc`, `dwnodllc`, `dwdll`, `dwimg`, `dwtrace`, `dwmain`, `dwtext`, and `dwreg`.
- Compiles setup and uninstall program modules/resources.
- Defines `zip` and `archive` targets for Win32 distribution packaging, including self-extracting archive text generated through `echogs`.

Dependencies and interactions:
- Must be acceptable to MSVC, Watcom, and Borland make dialects, so conditionals are limited.
- Used by Windows compiler-specific top-level makefiles.

Research relevance:
- Central Windows interpreter/resource/package build layer.

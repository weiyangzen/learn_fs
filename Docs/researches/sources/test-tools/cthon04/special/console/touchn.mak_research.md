# sources/test-tools/cthon04/special/console/touchn.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `TOUCHN.exe` variant for the Connectathon special `many-file create workload`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\TOUCHN.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.

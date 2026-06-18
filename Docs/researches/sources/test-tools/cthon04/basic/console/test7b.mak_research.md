# sources/test-tools/cthon04/basic/console/test7b.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test7b, the Connectathon basic link test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST7B.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test7b.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises link(), unlink(), stat(); rename fallback on DOS/Win32. It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().

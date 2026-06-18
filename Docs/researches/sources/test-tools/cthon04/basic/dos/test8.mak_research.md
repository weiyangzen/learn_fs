# sources/test-tools/cthon04/basic/dos/test8.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST8, the DOS build of the Connectathon basic symlink and readlink test.

Important APIs/types/functions: defines PROJ=TEST8, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST8.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises symlink(), lstat(), readlink(), unlink() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.

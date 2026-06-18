# sources/test-tools/cthon04/special/dos/nstat.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `NSTAT.EXE` variant for the Connectathon special `single-file stat timing test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=NSTAT`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\NSTAT.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.

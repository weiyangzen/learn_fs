# sources/test-tools/ior/src/ior-main.c

## Purpose
Provides the standalone executable entry point for IOR.

## Important APIs, Types, And Functions
Includes `ior.h` and defines `main(int argc, char **argv)`, which returns `ior_main(argc, argv)`.

## Control Flow
All substantive startup, MPI initialization, parsing, execution, reporting, and cleanup are delegated to `ior_main` in `ior.c`.

## State And Persistence Behavior
No state is owned here. Process exit status is the return value from `ior_main`, typically based on total error count.

## Dependencies And Integration Points
Links the executable target to the reusable IOR library-style function `ior_main`. This allows the same implementation to be invoked from tests or other embedding code through `ior_run`/`ior_main`.

## Risks And Edge Cases
Any change to `ior_main` signature or ownership of MPI initialization must be reflected here. The file intentionally has no direct MPI handling, so standalone behavior depends entirely on `ior.c`.

## Test Signals
Executable startup smoke tests, `ior -h`/option parsing, and MPI launcher runs validate this wrapper.

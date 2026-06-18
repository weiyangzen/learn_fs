# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.c

Implements ingestion and validation of trapping parameters from a Ghostscript parameter list.

Key behavior:
- `trap_put_float_param` reads a float parameter, applies a supplied validation predicate, signals parameter errors, and accumulates the current error code.
- `gs_settrapparams` copies the current trap parameter struct, reads known keys, validates unit-range and positive fields, reads booleans and integer fields, maps `ImageTrapPlacement` through enum names, and commits only if no error occurred.
- Validates `ImageResolution > 0`.

Dependencies:
- Uses `gs_param_list` helpers from `gsparamx.h` and trapping definitions from `gstrap.h`.

Research notes:
- The update is transactional at the struct level: the original parameters are replaced only after all reads and checks succeed.

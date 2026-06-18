# sources/security-integrity/selinux/libsepol/cil/src/cil_mem.c

## Purpose
`cil_mem.c` provides fail-fast allocation wrappers used throughout CIL.

## Important APIs, Types, And Functions
The module implements `cil_malloc`, `cil_calloc`, `cil_realloc`, `cil_strdup`, and `cil_asprintf`.

## Control Flow
Each wrapper calls the corresponding libc allocator or formatter. Allocation failure logs `Failed to allocate memory` and terminates with `exit(1)`. `cil_malloc(0)` and `cil_realloc(ptr, 0)` return NULL if libc does. `cil_strdup(NULL)` returns NULL.

## State And Persistence Behavior
The file owns no persistent state. It returns heap allocations to callers, and callers retain normal free/destroy responsibility.

## Dependencies And Integration Points
It depends on `cil_log` for error reporting. Nearly every CIL subsystem uses these wrappers, so allocation failures are treated as fatal process errors rather than recoverable `SEPOL_ERR` returns.

## Risks And Edge Cases
Fail-fast behavior is simple but makes low-memory testing and library embedding more difficult. `cil_asprintf` relies on `vasprintf`, which may require feature macros in some environments. Zero-size allocation behavior follows libc and can return NULL without logging.

## Test Signals
Normal tests mainly check successful allocation behavior indirectly. Fault-injection builds or allocator shims can confirm fatal OOM paths and NULL handling for zero-size and NULL strdup inputs.

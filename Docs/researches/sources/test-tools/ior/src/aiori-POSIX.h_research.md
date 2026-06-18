# sources/test-tools/ior/src/aiori-POSIX.h

## Purpose
Declares POSIX backend options and public helper functions used by the POSIX backend and by other IOR backends that delegate to POSIX for metadata or file lifecycle.

## Important APIs, Types, and Functions
- `posix_options_t` contains direct-I/O, Lustre, GPFS, BeeGFS, GPU Direct, and range-lock configuration fields.
- Lustre pool-name limit is selected from Lustre headers when available, otherwise a fallback value is used.
- Function declarations include `POSIX_Create`, `POSIX_Open`, `POSIX_Close`, `POSIX_Delete`, `POSIX_Rename`, `POSIX_Fsync`, `POSIX_Sync`, `POSIX_Mknod`, `POSIX_GetFileSize`, `POSIX_options`, `POSIX_check_params`, and `POSIX_xfer_hints`.

## Control Flow
The header has no executable control flow. Its declarations allow MMAP to reuse POSIX lifecycle functions and allow other modules to call POSIX metadata/file-size helpers through shared symbols.

## State and Persistence
No state is stored in the header. The layout of `posix_options_t` is runtime-significant because option allocation in `aiori-POSIX.c` and consuming modules cast `aiori_mod_opt_t *` to this type.

## Dependencies and Integration Points
Includes `aiori.h` and optional Lustre headers. Comments warn that MMAP depends on this option layout, especially the initial `direct_io` field.

## Risks and Edge Cases
- Duplicate `POSIX_check_params` declarations appear in the header.
- Changing `posix_options_t` layout can silently break MMAP or other casts.
- Feature-gated fields mean ABI/layout differs by build configuration.

## Test Signals
Compile all POSIX-dependent backends under feature combinations, validate no duplicate-prototype warnings become errors, and verify MMAP option compatibility after any struct changes.

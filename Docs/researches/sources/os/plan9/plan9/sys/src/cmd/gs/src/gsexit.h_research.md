# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsexit.h

## Role

`gsexit.h` declares exit/abort hooks that Ghostscript clients must provide.

## API

- `gs_to_exit(const gs_memory_t *mem, int exit_status)`
- `gs_to_exit_with_code(const gs_memory_t *mem, int exit_status, int code)`
- `gs_abort(const gs_memory_t *mem)`

## Semantics

`gs_to_exit` normally performs cleanup and error messaging without directly calling system `exit`, returning control to the caller.

`gs_to_exit_with_code` is similar but lets clients return the PostScript error code.

`gs_abort` handles fatal errors; after cleanup it may call `gp_do_exit`, which exits in a platform-independent way. The comments state returning from abort is not advisable.

## Dependencies

Requires `gs_memory_t`.

## Risks

These hooks are client-supplied. Embedders must implement them consistently with their ownership and process-lifetime model, especially for fatal paths.

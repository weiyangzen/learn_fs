# sources/user-network-fs/samba/source3/smbd/fd_handle.h

## Purpose
`fd_handle.h` declares the opaque fd-handle API used by smbd file structures.

## Important APIs, types, and functions
The header forward-declares `struct fd_handle` and exposes constructor, refcount, position-information, POSIX offset, generation-ID, and FSP fd helper functions: `fd_handle_create()`, `fh_get/set_refcount()`, `fh_get/set_position_information()`, `fh_get/set_pos()`, `fh_get/set_gen_id()`, `fsp_get_io_fd()`, `fsp_get_pathref_fd()`, and `fsp_set_fd()`.

## Control flow
Callers include the header to create handles for new FSPs and interact with fd-related state without knowing the struct layout. The opaque design keeps invariants in `fd_handle.c`.

## State and persistence behavior
No state is stored in the header. Runtime state lives in `struct fd_handle` instances allocated by `fd_handle_create()`.

## Dependencies and integration points
It includes `replace.h` and talloc declarations and depends on `files_struct` being visible to callers that use FSP helpers. It is included by connection/FSP allocation and I/O/close code.

## Risks and edge cases
- Because the struct is opaque, all new field access must be represented by explicit helpers.
- Callers must choose `fsp_get_io_fd()` versus `fsp_get_pathref_fd()` correctly.

## Test signals
Build coverage catches ABI/prototype drift. Runtime behavior is covered by `fd_handle.c` tests and higher-level FSP open/close/pathref tests.

# sources/user-network-fs/samba/source3/smbd/fd_handle.c

## Purpose
`fd_handle.c` implements the opaque shared fd-handle object used by `files_struct` instances to store an fd, reference count, current seek position, SMB position information, and generation ID.

## Important APIs, types, and functions
- `fd_handle_create()` allocates a handle initialized with fd `-1` and installs a destructor.
- `fh_get/set_refcount()`, `fh_get/set_position_information()`, `fh_get/set_pos()`, and `fh_get/set_gen_id()` expose opaque fields.
- `fsp_get_io_fd()` returns the fd for real I/O FSPs and rejects pathref FSPs.
- `fsp_get_pathref_fd()` returns the fd regardless of pathref status.
- `fsp_set_fd()` enforces fd assignment invariants.

## Control flow
The destructor asserts the fd has already been closed or is `AT_FDCWD`. `fsp_get_io_fd()` logs and, in developer builds, panics if a path-reference FSP is accidentally used for I/O. `fsp_set_fd()` allows setting the same fd, clearing to `-1`, assigning from `-1`, or setting `AT_FDCWD`, which accommodates VFS modules that assign the fd before the canonical helper does.

## State and persistence behavior
All state is process memory. The fd itself references kernel state but this file does not close it; close is handled by fd/FSP close paths.

## Dependencies and integration points
It depends on talloc and `files_struct` definitions. It is used throughout smbd for I/O position tracking, durable handle generation IDs, duplicate/open reference tracking, and pathref-versus-I/O separation.

## Risks and edge cases
- The destructor assertion catches leaked fds only when teardown reaches the handle.
- Pathref FSP misuse can become invalid-handle errors or developer panics.
- Reference count is manually managed by higher-level FSP code; this file does not enforce ownership.

## Test signals
Tests should validate initial values, getter/setter round trips, destructor assertion behavior with open fds, `fsp_get_io_fd()` rejecting pathrefs, and allowed/disallowed `fsp_set_fd()` transitions.

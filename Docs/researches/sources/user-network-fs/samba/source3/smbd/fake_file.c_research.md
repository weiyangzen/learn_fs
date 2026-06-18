# sources/user-network-fs/samba/source3/smbd/fake_file.c

## Purpose
`fake_file.c` implements pseudo-files that Windows clients expect but that are backed by Samba internal state rather than real filesystem objects, currently quota files when quota support is compiled in.

## Important APIs, types, and functions
- `struct fake_file_type` maps fake path prefixes to `enum FAKE_FILE_TYPE` and optional private-data initializers.
- `is_fake_file_path()` and `is_fake_file()` detect fake files by full SMB filename.
- `open_fake_file()` creates a `files_struct` with fd `-1`, initializes a fake-file handle, and calculates the effective access mask.
- `dosmode_from_fake_filehandle()` returns Windows-compatible attributes for quota fake files.
- `close_fake_file()` is a no-op because fake files hold no fd resources.

## Control flow
Path detection compares the start of the full SMB filename to configured fake-file names. Opening requires the effective UID to be Samba's initial/root UID, allocates a normal FSP, marks it non-lockable, sets fnum/vuid/access/name state, initializes type-specific private data, and calls `smbd_calculate_access_mask_fsp()` to enforce normal access semantics before returning the FSP.

## State and persistence behavior
Fake file state is in-memory in `fsp->fake_file_handle` and its optional private data. No real fd is opened and `close_fake_file()` does not persist anything. Quota private data may reflect quota subsystem state outside this file.

## Dependencies and integration points
It depends on `fake_file.h`, auth/current UID helpers, file allocation, access-mask calculation, and optional quota initialization. Close dispatch in `close.c` and DOS mode logic in `dosmode.c` special-case fake file handles.

## Risks and edge cases
- Prefix matching means fake names must be unique and not collide with ordinary paths.
- Open is allowed only while privileged; wrong privilege state causes access denied.
- Non-quota fake-handle type in `dosmode_from_fake_filehandle()` logs an error and returns normal attributes.
- Fake FSPs have fd `-1` and cannot lock; callers must route operations through fake-file-aware paths.

## Test signals
Tests should cover fake path detection, non-fake paths, open privilege failure, quota fake file open with expected attributes, access-mask calculation failure cleanup, and close dispatch without fd operations.

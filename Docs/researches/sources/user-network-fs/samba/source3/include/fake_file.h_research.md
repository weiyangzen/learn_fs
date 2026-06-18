# sources/user-network-fs/samba/source3/include/fake_file.h

## Purpose
`fake_file.h` declares support for synthetic server-side files that Windows clients expect but that are not normal filesystem objects, such as quota metadata or named pipe proxies.

## Important APIs, Types, And Functions
- `enum FAKE_FILE_TYPE` distinguishes none, quota, and named pipe proxy fake files.
- Quota fake file path constants define Win32 and Unix spellings for `$Extend/$Quota:$Q:$INDEX_ALLOCATION`.
- `struct fake_file_handle` stores fake file type and private data.
- `is_fake_file_path()` and `is_fake_file()` classify paths.
- `open_fake_file()` opens a fake file as a Samba `files_struct`.
- `close_fake_file()` closes fake file state.
- `dosmode_from_fake_filehandle()` exposes DOS attributes for fake handles.

## Control Flow
SMB open paths classify a requested path, call `open_fake_file()` instead of normal VFS open for supported synthetic objects, and later call `close_fake_file()` during handle teardown.

## State And Persistence
Fake handles carry private in-memory state. Backing data may come from quota or pipe subsystems, but this header does not define persistent storage.

## Dependencies And Integration Points
It integrates SMB request handling, connection state, `smb_filename`, `files_struct`, quota support, and named pipe proxy logic.

## Risks
Fake file paths must be recognized consistently across slash styles. Access mask enforcement and DOS mode reporting are security-sensitive because these objects bypass normal filesystem lookup.

## Test Signals
Test fake path detection with Win32/Unix spellings, open/close lifecycle, quota read semantics, named pipe proxy routing, access-denied cases, and DOS mode output.

# sources/user-network-fs/samba/source4/torture/smb2/mkdir.c

## Purpose
`mkdir.c` is a compact SMB2 directory create/remove behavior test. It checks normal mkdir/rmdir, collisions, file-versus-directory status codes, invalid path syntax, and missing parent path handling.

## Important APIs, Types, and Functions
The only test function is `torture_smb2_mkdir()`. It uses `smb2_util_setup_dir()`, `smb2_util_mkdir()`, `smb2_util_rmdir()`, `smb2_create_complex_file()`, `smb2_util_unlink()`, and `smb2_deltree()`. The base directory is `mkdirtest`, and the main target path is `mkdirtest\\mkdir.dir`.

## Control Flow
The test creates the base directory, creates `mkdir.dir`, verifies a second mkdir returns `NT_STATUS_OBJECT_NAME_COLLISION`, removes it, verifies a second rmdir returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`, creates a file at the same path, verifies mkdir collides with the file, verifies rmdir of the file returns `NT_STATUS_NOT_A_DIRECTORY`, removes the file, then checks `..\\..\\..` and a missing nested parent path for syntax/path-not-found errors.

## State and Persistence Behavior
All server-side state is temporary under `mkdirtest`. Cleanup always calls `smb2_deltree()` on the base directory.

## Dependencies and Integration Points
This test depends on SMB2 utility wrappers from the torture suite and is likely registered by the broader SMB2 torture initialization code rather than defining a local suite.

## Risks and Edge Cases
Expected status codes are precise and may expose server differences in path normalization, dot-dot handling, or file/directory collision mapping. If base directory setup fails, later assertions do not run.

## Test Signals
The meaningful signals are exact NTSTATUS values for create collision, missing remove target, rmdir-on-file, bad path syntax, and missing parent directory.

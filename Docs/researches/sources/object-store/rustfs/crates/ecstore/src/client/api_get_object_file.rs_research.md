# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_file.rs

## Purpose
Intended to implement `fget_object`, downloading an object to a local file through a temporary `.part.rustfs` path with resume support.

## Important APIs, Types, and Functions
- `TransitionClient::fget_object(bucket, object, file_path, opts)` validates the target path, creates parent directories, stats the object, computes a part path, opens the part file, optionally sets a range on Windows, calls `get_object`, and renames the part file to the final path.

## Control Flow and State Behavior
The method first requires `std::fs::metadata(file_path)` to succeed; if the file does not exist it returns an error. It creates a directory from `parent.file_name()` rather than the full parent path. It opens the temp part path without create/write options, then calls the currently unsupported `get_object`. The actual copy from object reader to file is commented out, as is cleanup logic.

## Dependencies and Integration Points
Depends on `GetObjectOptions`, `TransitionClient::stat_object`, `TransitionClient::get_object`, local filesystem APIs, platform-specific metadata extensions, and `err_invalid_argument`.

## Persistence
This is the only file in the subset that directly mutates local filesystem state. Intended persistence is a downloaded object file via temp-file rename, but the copy path is currently disabled.

## Risks and Edge Cases
The function is not operational: it errors if the destination does not already exist, opens the part file without creating it, does not copy bytes, relies on unsupported `get_object`, and may rename an empty/old part file. Parent directory creation uses only the last path component. Cleanup is commented out, so partial files may remain. Permissions are set on a copied metadata object without writing them back with `set_permissions`.

## Test Signals
No inline tests. Tests should cover new-file downloads, existing-directory errors, parent directory creation, temp-file cleanup, resume behavior, and integration after `get_object` is implemented.

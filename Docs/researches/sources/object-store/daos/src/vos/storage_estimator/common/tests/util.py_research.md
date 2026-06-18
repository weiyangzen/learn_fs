# sources/object-store/daos/src/vos/storage_estimator/common/tests/util.py

## Purpose
Small filesystem fixture helper for storage-estimator tests. `FileGenerator` creates a temporary mock DFS-like directory tree containing directories, sparse files, and symlinks, then cleans it up.

## Important APIs, types, and functions
- `FileGenerator.__init__(prefix="")` creates a temp directory and sets `_mock_root` to `<tmp>/daos`.
- `get_root()` returns the mock root path.
- `crete_mock_fs(files)` prints the temp path and delegates to `_create_files`; the method name is misspelled but is likely part of local test API.
- `_create_files()` dispatches dictionaries with `type` equal to `dir`, `file`, or `symlink`.
- `generate_file()` creates parent directories and writes one byte at `size - 1`, producing sparse files.
- `clean()` and `__del__()` remove the mock root.

## Control flow
Tests instantiate `FileGenerator`, pass a list of file descriptors, and then run estimator exploration against `get_root()`. Each descriptor is handled independently. Files cause parent directory creation before sparse write; symlinks are created directly at target path.

## State and persistence behavior
State is limited to temporary filesystem contents under `_mock_root`. Generated files are sparse and store only one byte at the end, so apparent file size is controlled without allocating full data. Cleanup deletes the whole mock root; double cleanup can raise if `__del__` runs after manual `clean()` removed it.

## Dependencies and integration points
Depends on Python `tempfile`, `os`, and `shutil`. Integrates with `FileSystemExplorer` tests by providing realistic `os.walk`/stat/symlink targets.

## Risks and edge cases
`generate_file` with size 0 seeks to `-1`, which would fail. `_create_symlink` does not ensure parent directories exist, so callers must list directory creation before symlinks. `__del__` unconditionally calls `clean()`, so tests that call `clean()` manually may need to tolerate cleanup errors.

## Test signals
Signals are correct directory tree creation, sparse file sizes visible to stat, symlink presence and target string length, and cleanup after estimator tests.

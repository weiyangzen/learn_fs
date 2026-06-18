# sources/sync-backup/git-lfs/t/t-clean.sh

## Purpose
Unit-style integration tests for `git lfs clean`, the clean filter that stores file contents in the LFS object store and emits pointer files. It also covers pointer-like inputs, pointer extensions, and stdin handling.

## Important APIs, Functions, and Control Flow
`clean_setup` creates a Git repository. Tests pipe ordinary content, a valid pointer, pseudo-pointers, and a pseudo-pointer with large extra data through `git lfs clean`, then compare exact pointer output. The pointer-extension test configures a case-inverter extension and verifies the extension pointer and local object. The stdin test compares OIDs from `git lfs clean < file` to `calc_oid_file`.

## State, Persistence, and Dependencies
The command writes objects under `.git/lfs/objects`, and the extension test writes `LFSTEST_EXT_LOG`. Dependencies include `pointer`, `calc_oid`, `calc_oid_file`, `setup_case_inverter_extension`, `case_inverter_extension_pointer`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with the clean filter, pointer parser, object storage, and extension clean hook. Signals are exact pointer comparisons, object assertions, and extension log entries. Risks include exact fixture hashes and buffer-sensitive pseudo-pointer behavior.

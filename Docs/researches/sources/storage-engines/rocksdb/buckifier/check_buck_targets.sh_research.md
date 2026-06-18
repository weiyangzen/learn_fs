# sources/storage-engines/rocksdb/buckifier/check_buck_targets.sh

## Purpose

`check_buck_targets.sh` is a repository consistency check for generated RocksDB Buck targets. It verifies that the committed `BUCK` file matches the output of `buckifier/buckify_rocksdb.py` and instructs contributors to regenerate rather than hand-edit `BUCK`.

## Control Flow

1. Require a `BUCK` file in the current working directory. If missing, print guidance and exit `1`.
2. Check whether `BUCK` already has uncommitted changes with `git diff BUCK | head -n 1`.
3. If `BUCK` is dirty before the check starts, print that the check is skipped and exit `0`.
4. Copy `BUCK` to `BUCK.bkp`.
5. Run `${PYTHON:-python3} buckifier/buckify_rocksdb.py`.
6. Require that `BUCK` still exists after generation.
7. Check `git diff BUCK | head -n 1` again.
8. If there is no diff, restore `BUCK.bkp` over `BUCK` and exit `0`.
9. If there is a diff, print regeneration instructions and the Python version, restore `BUCK.bkp`, and exit `1`.

## State and Persistence Behavior

The script temporarily writes `BUCK.bkp` in the repository root and rewrites `BUCK` by invoking the buckifier. On normal success and on detected diff failure, it restores the original `BUCK` content from the backup.

It does not use `trap`, so interruption or an unexpected shell/runtime failure after `cp BUCK BUCK.bkp` can leave `BUCK.bkp` behind and may leave generated `BUCK` content in place.

## Dependencies and Integration Points

- Must be run from the RocksDB repository root because it expects `BUCK` and `buckifier/buckify_rocksdb.py` at relative paths.
- Uses `git diff BUCK` to detect dirtiness and generated changes.
- Uses `cp` and `mv` for backup/restore.
- Honors the `PYTHON` environment variable, defaulting to `python3`.
- Depends on `buckify_rocksdb.py` and all of that script's source-manifest and JSON inputs.

## Risks and Edge Cases

- Pre-existing uncommitted `BUCK` changes cause a skip with success status. That avoids overwriting user changes but can let CI miss stale generated targets if the workspace is already dirty.
- The backup restore is duplicated in success/failure branches but not protected by `trap`; termination between generation and restore is unsafe.
- `TGT_DIFF` uses backticks and `[ ! -z "$TGT_DIFF" ]`; it works for this simple check but is less robust than `[[ -n "$TGT_DIFF" ]]`.
- The script only verifies `BUCK`, not benchmark runtime correctness or actual Buck target buildability.
- If the buckifier exits nonzero, `set -e` is not enabled, so the script continues to the post-generation checks. Depending on the partial `BUCK` state, this may still fail by diff, but the original generator error is not surfaced directly.

## Test Signals

The script itself is the main test signal for buckifier determinism. A clean run exits `0` with no generated diff. A stale `BUCK` exits `1` after printing the command to regenerate. Missing `BUCK` also exits `1`.

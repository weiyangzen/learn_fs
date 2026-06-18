# sources/security-integrity/encfs/tests/rename_symlink_in_dir_test.rs

Purpose: regression tests for renaming directories that contain symlinks when chained name IV is enabled. The target bug was recursive directory copy/rename failing or not re-encrypting symlink targets correctly.

Important APIs/types/functions: `setup_fs` creates default `EncFs` with chained name IV, `req` supplies request metadata, and tests use `mkdir`, `symlink`, `create`, `release`, `readlink`, `rename`, and `getattr`.

Control flow: `test_rename_directory_containing_symlink_with_chained_name_iv` creates `/parent` with a symlink and file, validates readlink before rename, renames to `/renamed_parent`, then validates readlink, old path absence, and regular file presence. `test_rename_nested_directory_with_symlinks_chained_name_iv` creates `/outer/inner` with symlinks at both levels, renames `/outer` to `/moved`, and verifies both symlink targets still decrypt to the original relative targets.

State and persistence: creates temp backing trees and removes them.

Dependencies and integration points: depends on directory rename implementation, recursive copy/delete behavior, symlink encryption/decryption, and name-IV recalculation.

Risks: uses direct trait calls rather than a kernel mount, so it does not cover lookup cache effects. Only default config is tested.

Test signals: high-value integrity signal for directory rename with symlink children under IV-chained name encryption.

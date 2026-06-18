# sources/object-store/rustfs/crates/ecstore/src/set_disk/multipart.rs

## Purpose
Provides set-level multipart upload discovery and validation helpers. It lists committed part numbers that are present on quorum drives and verifies that a multipart upload ID has valid metadata quorum.

## Important APIs, Types, And Functions
`collect_list_parts_results` runs per-disk listing tasks with early failure when read quorum becomes impossible. `empty_upload_fallback_possible` distinguishes empty/missing upload directories from ordinary quorum failures. `reduce_quorum_part_numbers` only returns part numbers that have both `part.N` and `part.N.meta` on at least read quorum drives. `SetDisks::list_parts` and `check_upload_id_exists` are the exposed helpers.

## Control Flow
`list_parts` calls `DiskAPI::list_dir` against `RUSTFS_META_MULTIPART_BUCKET`, collects per-disk results, reduces read errors, and then reduces the returned filenames into sorted quorum part numbers. `check_upload_id_exists` maps upload ID to its multipart metadata path, reads all file info, maps `FileNotFound` to `InvalidUploadID`, computes object quorum, optionally checks write quorum, selects online disks by metadata consensus, and returns the authoritative upload `FileInfo` with all disk metadata.

## State And Persistence Behavior
This file is read-only. It inspects multipart metadata in the internal multipart bucket and does not mutate upload state.

## Dependencies And Integration Points
It depends on metadata path helpers, disk list/read APIs, quorum reducers, `OBJECT_OP_IGNORED_ERRS`, `FileInfo`, and storage error mapping. It is consumed by higher-level multipart upload handlers for listing parts, completing uploads, and validating upload IDs.

## Risks
The collector treats panicked tasks as non-successes but only fails once quorum is impossible; this is intentional but can obscure a systemic panic if quorum still succeeds. `reduce_quorum_part_numbers` requires both payload and `.meta`, so partial stale metadata is excluded. Empty-upload fallback must stay aligned with S3 multipart semantics.

## Test Signals
Tests cover early quorum failure, tolerance of one panicked task when quorum is met, `FileNotFound` fallback for empty upload dirs, early failure when fallback is impossible, and quorum filtering of part numbers.

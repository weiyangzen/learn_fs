# sources/object-store/rustfs/crates/ecstore/src/set_disk/write.rs

## Purpose
Implements set-level write-side quorum helpers for object data, multipart parts, metadata updates, dangling deletes, prefix deletion, and HTTP precondition checks.

## Important APIs, Types, And Functions
Key methods are `default_read_quorum`, `default_write_quorum`, `rename_data`, `commit_rename_data_dir`, `cleanup_multipart_path`, `rename_part`, `eval_disks`, `write_unique_file_info`, `update_object_meta`, `update_object_meta_with_opts`, `delete_if_dangling`, `delete_prefix`, and `check_write_precondition`.

## Control Flow
`rename_data` fans out per-disk `rename_data`, records old data dirs/signatures, rolls back successful writes with `delete_version(... undo_write ...)` if write quorum fails, then returns online disks, common old data dir, and cleanup candidates. `rename_part` clears stale destination part paths, renames temp part payload and metadata, cleans up on quorum failure, and returns successful disks. Metadata writes fan out and revert successful metadata on quorum failure. `check_write_precondition` reads current object info without taking a lock and applies If-Match/If-None-Match logic.

## State And Persistence Behavior
This file writes and deletes persisted object metadata/data across disks. Rollback is best effort and quorum-driven. `delete_if_dangling` writes delete-version markers for dangling/corrupt object states and annotates diagnostic tags in memory. `delete_prefix` recursively removes a prefix with majority write quorum.

## Dependencies And Integration Points
It depends on disk write APIs, quorum reducers, multipart bucket constants, object options, metadata update options, path helpers, global processors, and object-info read paths. It is called by object and multipart handlers and by healing.

## Risks
Partial rollback failures can leave mixed old/new data dirs. `cleanup_multipart_path` logs but does not surface delete failures before overwrite. `delete_if_dangling` builds diagnostic tags that are not audited yet. Preconditions rely on callers already holding any required write lock, as stated in the comment.

## Test Signals
No local tests in this file. Tests should cover rename rollback on quorum failure, multipart overwrite cleanup, metadata replacement with `replace_user_metadata`, dangling delete decisions, and precondition behavior for delete markers and missing objects.

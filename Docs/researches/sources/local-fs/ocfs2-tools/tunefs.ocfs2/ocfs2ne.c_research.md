# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/ocfs2ne.c

## Role

`tunefs.ocfs2` front controller. This file owns command-line parsing, option-to-operation dispatch, operation ordering, progress setup, filesystem open/reopen policy, and the main program entrypoint.

## Main Structures

- `struct tunefs_option`: wraps `getopt_long()` metadata, help text, operation pointer, parse handler, seen flag, and private option state.
- `struct tunefs_journal_option`: maps `-J` journal sub-options such as `size`, `block64`, and `block32` to tunefs operations.
- `struct tunefs_run`: linked-list entry for queued operations.
- Global `tunefs_run_list`: ordered list of operations to execute.
- Global `tunefs_op_count` and `tunefs_op_progress`: top-level progress accounting.

## Operation Registration

External operations declared here include sparse listing, query, UUID reset, feature toggles, resize, journal size/block mode changes, label changes, slot count changes, cluster stack update, cloned volume handling, and quota sync interval changes.

The option table maps user-visible flags to those operations:

- `-Q/--query` -> `query_op`
- `--list-sparse` -> `list_sparse_op`
- `-U/--uuid-reset[=uuid]` -> `reset_uuid_op`
- `--update-cluster-stack` -> `update_cluster_stack_op`
- `--cloned-volume[=label]` -> `cloned_volume_op`
- `-N/--node-slots` -> `set_slot_count_op`
- `-L/--label` -> `set_label_op`
- `--fs-features` plus derived feature aliases -> `features_op`
- `-S/--volume-size` -> `resize_volume_op`
- `-J/--journal-options` -> journal operation table
- `--usrquota-sync-interval` / `--grpquota-sync-interval` -> quota interval ops

## Parsing Flow

`build_options()` dynamically builds both short and long getopt tables from the `options[]` array. Long-only options initially use `CHAR_MAX`; the builder assigns unique unprintable values above `CHAR_MAX`.

`parse_options()` loops through `getopt_long()`, rejects duplicate options except verbosity handlers that explicitly clear `opt_set`, calls any `opt_handle`, and appends `opt_op` to the run list. It then folds feature-oriented options into one feature string via `parse_feature_strings()`, validates the device argument, and invokes `parse_resize()` for historical resize syntax where the new size may be a trailing positional argument.

## Special Cases

Feature parsing is delayed until after all options are processed. `-M local`, `-M cluster`, `--backup-super`, and `--fs-features` all contribute strings to one final `features_op`.

Resize is prepended, not appended. `parse_resize()` queues `resize_volume_op` at the head so filesystem growth happens before later operations that may need newly available space.

Journal sub-options are parsed as comma-separated `name[=value]` tokens. Unknown options cause the valid journal sub-option list to be printed.

## Execution Flow

`run_operations()` repeatedly computes combined open flags from pending operations, opens the filesystem with `tunefs_open()`, and then decides which subset can run:

- `TUNEFS_ET_CLUSTER_SKIPPED`: run only `TUNEFS_FLAG_SKIPCLUSTER` operations, mainly cloned volume handling.
- `TUNEFS_ET_INVALID_STACK_NAME`: run only `TUNEFS_FLAG_NOCLUSTER` operations, mainly cluster stack update.
- `TUNEFS_ET_PERFORM_ONLINE`: run online-capable operations before failing offline-only operations.
- Normal open: run remaining operations in queued order.

After each pass it closes and, if needed, reopens the filesystem so metadata changes such as UUID or cluster-stack updates are reflected before continuing.

## Safety Model

The file itself does not perform metadata writes; it sequences operations and delegates write safety to `tunefs_open()`, `tunefs_op_run()`, and each operation implementation. It does preserve important ordering constraints: cloned volume and cluster-stack repair can unblock later normal opens, online-capable operations can still run on mounted filesystems, and resize happens before space-consuming changes.

## Dependencies

Uses `libocfs2ne.h` for tunefs abstractions, progress, verbosity, interaction, open/close, operation execution, and error codes. Uses `ocfs2/ocfs2.h` and list helpers from the OCFS2 userspace library.

## Notable Risks

- Duplicate operation instances can be queued through different options if the option layer allows it, although duplicate exact options are rejected.
- `parse_feature_strings()` returns `errcode_t` but locally uses integer-style `rc`; functionally this works for success/failure but blurs error-code fidelity.
- `handle_journal_arg()` appends operations as it parses. If later journal tokens fail, already-appended operations remain on the run list before `print_usage()` exits the process, so this is not observable in normal execution but matters for reuse.

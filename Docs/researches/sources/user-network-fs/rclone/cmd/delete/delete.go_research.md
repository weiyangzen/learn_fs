<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/delete/delete.go -->
# sources/user-network-fs/rclone/cmd/delete/delete.go

## Purpose

`delete.go` implements `rclone delete`, deleting files under a remote path while respecting filters and optionally removing empty directories.

## Important APIs, Types, and Functions

The `rmdirs` flag controls empty directory cleanup. The Cobra command validates one argument, resolves the source with `cmd.NewFsSrc`, and calls `operations.Delete` inside `cmd.Run(true, false, ...)`. If `--rmdirs` is set and delete succeeds, it calls `operations.Rmdirs` with the root-preserving argument.

## Control Flow

Delete runs first; directory cleanup is conditional and only attempted after file deletion returns nil.

## State and Persistence Behavior

It mutates remote state by deleting filtered files and possibly empty directories. Dry-run and interactive behavior are enforced by lower layers.

## Dependencies and Integration Points

It integrates with global filters, Fs source helper, operations delete/rmdirs, and retry/accounting behavior.

## Risks and Test Signals

Risks include accidental data loss from filters, retrying partial deletes, misunderstanding that directories are preserved by default, and root removal policy. Tests should cover filters, dry-run, rmdirs flag, delete errors blocking rmdirs, retries, and directory-only paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/delete/delete.go -->

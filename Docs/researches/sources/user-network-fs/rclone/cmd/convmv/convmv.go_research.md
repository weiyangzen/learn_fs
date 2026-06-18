<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv.go -->
# sources/user-network-fs/rclone/cmd/convmv/convmv.go

## Purpose

`convmv.go` implements `rclone convmv`, converting object and directory names in place with the global `--name-transform` pipeline.

## Important APIs, Types, and Functions

The command registers `--delete-empty-src-dirs` and `--create-empty-src-dirs`. Its Cobra `Run` validates one destination, resolves it with `cmd.NewFsFile`, requires `transform.Transforming(context.Background())`, and chooses `sync.Transform` for directory roots or `operations.TransformFile` for single files.

## Control Flow

Execution is under `cmd.Run(false, true, ...)`. The command refuses to run unless a name transform has been configured by global transform flags. Directory transforms can remove or create empty dirs depending on flags.

## State and Persistence Behavior

It mutates remote object and directory names in place, with potential deletes for empty source dirs and creates for empty destination dirs. No local persistent files are written.

## Dependencies and Integration Points

It integrates with the root transform option system, `fs/sync.Transform`, `operations.TransformFile`, and Fs resolution helpers.

## Risks and Test Signals

Risks include data loss from name collisions, non-idempotent transforms, Unicode normalization surprises, directory/file tag confusion, and concurrency races when many inputs map to one output. Tests should cover no-transform rejection, file vs directory paths, dry-run behavior through operations, empty directory flags, conflict handling, and reversible transform cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv.go -->

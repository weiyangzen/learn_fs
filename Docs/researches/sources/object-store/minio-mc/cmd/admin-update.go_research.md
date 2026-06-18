# sources/object-store/minio-mc/cmd/admin-update.go

## Purpose

`admin-update.go` implements `mc admin update`, which asks a MinIO cluster to update all servers, optionally using a supplied update URL.

## Important APIs, Types, and Functions

`adminUpdateFlags` defines `--yes/-y`. `adminServerUpdateCmd` wires the command. `serverUpdateMessage` wraps `madmin.ServerUpdateStatusV2` and renders host-level results in a table. `mainAdminServerUpdate` performs confirmation and calls `ServerUpdateV2`.

## Control Flow

The handler validates one or two args, builds an admin client, reads the optional update URL from arg 2, prompts for confirmation on terminals unless `--yes` is set, and aborts on non-yes answers. It then calls `client.ServerUpdateV2` with `DryRun` and `UpdateURL`, and prints the formatted update result.

## State and Persistence Behavior

No local state is persisted. The command triggers remote update state and renders per-peer statuses, including upgraded versions, errors, and waiting drives.

## Dependencies and Integration Points

It uses `newAdminClient`, `madmin.ServerUpdateOpts`, terminal input, console/table formatting, `fatalIf`, and global flags. It references `ctx.Bool("dry-run")` even though this file only declares `--yes`, so it depends on a global or shared dry-run flag if present.

## Risks and Edge Cases

Cluster update is disruptive, so terminal confirmation is important. Non-terminal runs without `--yes` proceed without prompting. Missing or absent dry-run flag registration would make `ctx.Bool("dry-run")` inert. Waiting drives are reported as upgraded but needing OS reboot.

## Test Signals

Tests should cover arity, confirmation yes/no handling, non-terminal behavior, update URL propagation, message rendering for success/error/waiting drives, and JSON output.

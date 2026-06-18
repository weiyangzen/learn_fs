<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch_test.go -->
# sources/user-network-fs/rclone/cmd/touch/touch_test.go

## Purpose

`touch_test.go` validates `Touch` command behavior against the fstest remote harness and local backend registration.

## Important APIs, Types, and Functions

The test helper `checkFile` compares remote contents and modtime using `timeOfTouch`. `TestMain` initializes fstest. Individual tests cover new-file creation, `--no-create`, timestamp parsing, updating existing objects, nested path creation, empty names/directories, shallow and recursive directory touching, and metadata creation.

## Control Flow

Each test creates an isolated `fstest.NewRun`, mutates global command flags as needed, calls `Touch` directly, and validates remote listing/object metadata. Metadata tests temporarily modify `fs.ConfigInfo.Metadata` and `MetadataSet` and restore them with `t.Cleanup`.

## State and Persistence Behavior

The file intentionally manipulates package globals (`notCreateNewFile`, `timeAsArgument`, `recursive`) and global config. Some flag resets are manual, making isolation important when tests fail early.

## Dependencies and Integration Points

It depends on `fstest`, `backend/local`, `fs.Metadata`, and testify `require`. It exercises user-visible command logic without Cobra parsing.

## Risks and Test Signals

The suite signals expected behavior for missing paths, existing files, directories, recursion, and metadata. Gaps include explicit invalid timestamp errors, `--localtime`, dry-run/interactive skip paths, and backend precision variations beyond `fs.ModTimeNotSupported` checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch_test.go -->

# sources/user-network-fs/blobfuse2/azure-pipeline-templates/bfusemon.yml

## Purpose
This Azure DevOps template validates Blobfuse2 health monitor integration by mounting with monitoring enabled, exercising file operations, and printing monitor JSON output.

## Important APIs, Types, and Functions
It calls `blobfuse2 gen-test-config` with `azure_key_hmon.yaml`, symlinks `bfusemon` into `/usr/local/bin`, mounts through the shared `mount.yml` template, and cleans up through `cleanup.yml`.

## Control Flow
The template creates a key-based block config with `HMON_OUTPUT`, creates mount and cache directories, mounts Blobfuse2 after installing the `bfusemon` symlink, prints process information, performs create/copy/mkdir/move/delete operations on the mount, waits, prints `monitor_*.json`, then unmounts without deleting containers.

## State and Persistence Behavior
It mutates `/usr/local/bin/bfusemon`, writes config and monitor JSON in `$(WORK_DIR)`, and uses `$(MOUNT_DIR)` and `$(TEMP_DIR)`. No long-term storage state is intended beyond operations against the test container.

## Dependencies and Integration Points
It depends on `build.yml` having built both `blobfuse2` and `bfusemon`, on block account variables, and on the common mount/cleanup templates.

## Risks and Edge Cases
The symlink requires sudo and may collide with an existing `bfusemon`. The test prints generated config and monitor output. It validates monitor presence but not structured JSON fields beyond manual log inspection.

## Test Signals
Signals include a running `bfusemon` process, successful file operations, `monitor_*.json` containing health output, and clean unmount.

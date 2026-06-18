# sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount.yml

## Purpose
This shared template standardizes pre-mount cleanup, mount execution, wait, process visibility, and optional mount directory cleanup.

## Important APIs, Types, and Functions
Parameters include a step-valued `mountStep`, display `prefix`, and `ro_mount`. It composes `cleanup.yml`, runs the supplied mount step, sleeps, prints `ps` output, and conditionally clears `$(MOUNT_DIR)/*`.

## Control Flow
Each use first unmounts and avoids container deletion, executes the caller-provided mount command, waits ten seconds, prints Blobfuse2 processes, and if not a read-only mount, removes existing files under the mount as pre-start cleanup.

## State and Persistence Behavior
It mutates the active mount and may delete all files under `$(MOUNT_DIR)` after mounting. It relies on caller-owned Azure container state.

## Dependencies and Integration Points
Most test templates call this before running filesystem operations. It centralizes the mount lifecycle for E2E, data, FIO, stress, scenario, and health monitor tests.

## Risks and Edge Cases
Because cleanup of mount contents happens after mounting, an accidental wrong mount path or failed unmount can delete local or remote data. The `ro_mount` flag must be set correctly for read-only validation.

## Test Signals
Signals are successful mount command completion, visible Blobfuse2 process, and clean pre-start directory state for write tests.

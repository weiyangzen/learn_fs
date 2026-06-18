# File Research: sources/windows/windows-driver-samples/filesys/cdfs/shutdown.c

## Purpose

Implements CDFS shutdown handling. It purges mounted volumes, forwards shutdown to underlying storage stacks, attempts dismount, and unregisters the filesystem device.

## Main Entry Point

- `CdCommonShutdown`

## Key Behavior

The routine disables popups, marks global CDFS shutdown state, acquires global CDFS data, and walks the global VCB queue. It skips volumes already shut down or not mounted.

For each mounted volume, it acquires the VCB exclusively, purges the volume, builds a synchronous `IRP_MJ_SHUTDOWN` for the target device stack, calls the target driver, waits if pending, clears the event, marks the VCB shutdown, and calls `CdCheckForDismount`.

After all volumes are processed, it releases global CDFS data, unregisters and deletes the filesystem device object, then completes the original shutdown IRP with success.

## Dependencies

Uses global VCB queue locking, purge/dismount support, synchronous FSD request construction, lower-device dispatch, and filesystem registration cleanup.

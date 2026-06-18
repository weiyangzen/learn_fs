# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.h

This header contains constants shared by the OS/2 PM Ghostscript display driver, the external `gspmdrv` process, and PM GSview.

It defines named object format strings for OS/2 interprocess communication:

- `SHARED_NAME` for shared bitmap memory.
- `SYNC_NAME` and `NEXT_NAME` for event semaphores.
- `MUTEX_NAME` for the bitmap mutex semaphore.
- `QUEUE_NAME` for driver message queues.

It also defines integer message IDs exchanged over the queues:

- `GS_UPDATING`
- `GS_SYNC`
- `GS_PAGE`
- `GS_CLOSE`
- `GS_ERROR`
- `GS_PALCHANGE`
- `GS_BEGIN`
- `GS_END`

These values are consumed by `gdevpm.c` when it posts display-update, synchronization, page, palette-change, and lifecycle events to GSview or `gspmdrv.exe`.

Filesystem relevance: none. This is OS/2 IPC naming and message protocol metadata for a display driver.

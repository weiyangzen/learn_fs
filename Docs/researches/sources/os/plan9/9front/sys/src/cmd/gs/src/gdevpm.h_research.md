# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.h

Small shared header for the OS/2 Presentation Manager Ghostscript driver, its companion `gspmdrv.c`, and PM GSview integration.

Key contents:
- Defines named shared-memory, semaphore, mutex, and queue path templates: `SHARED_NAME`, `SYNC_NAME`, `NEXT_NAME`, `MUTEX_NAME`, and `QUEUE_NAME`.
- Defines queue message codes used between Ghostscript, GSview, and the PM driver: `GS_UPDATING`, `GS_SYNC`, `GS_PAGE`, `GS_CLOSE`, `GS_ERROR`, `GS_PALCHANGE`, `GS_BEGIN`, and `GS_END`.

Notable dependencies:
- No included Ghostscript types; this header is only constants and include guards.

Research notes:
- The file is tightly coupled to `gdevpm.c` and the outboard OS/2 display process.

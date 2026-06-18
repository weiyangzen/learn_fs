# File Research: sources/windows/reactos/ntoskrnl/mm/shutdown.c

Read completely: 100 lines.

This file implements memory-manager shutdown phases. `MiShutdownSystem` first frees page-file name buffers and closes page-file handles, then repeatedly scans legacy-Mm LRU user pages and flushes dirty data-file section pages through `MmCheckDirtySegment(..., PageOut=TRUE)` until a pass finds no dirty pages.

`MmShutdownSystem` dispatches by phase: phase 0 runs `MiShutdownSystem`, phase 1 dereferences paging-file `FileObject`s, and phase 2 is explicitly `UNIMPLEMENTED`. The dirty flush loop dereferences any segment association returned for each page after checking/writing it.

Important interactions: depends on `MmNumberOfPagingFiles`, `MmPagingFile`, LRU page enumeration, `MmGetSectionAssociation`, section segment locking, segment page entries, and the dirty-page writeback logic in `section.c`.

Security/reliability notes: shutdown correctness depends on `MmCheckDirtySegment` being able to flush data-file pages even while filesystem code may dirtify more pages. Phase 2 being unimplemented means final memory-manager shutdown behavior is incomplete. Closing paging-file handles before later dereferencing file objects is intentional but fragile if ordering changes.

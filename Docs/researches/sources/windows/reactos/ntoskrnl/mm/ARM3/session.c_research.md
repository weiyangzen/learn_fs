# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/session.c

Read status: complete file, 1089 lines.

This file implements ARM3 session-space lifecycle support: session ID allocation, session-space page/table setup, working-set initialization, process membership accounting, session attach/detach, locale storage, and lookup of a process belonging to a session.

Key entry points:
- `MiInitializeSessionWsSupport()` initializes the global session working-set list.
- `MiInitializeSessionIds()` computes per-session data/tag/page charges, initializes `MiSessionIdMutex`, and allocates the initial session-ID bitmap.
- `MmIsSessionAddress()`, `MmGetSessionLocaleId()`, `MmSetSessionLocaleId()`, `MmGetSessionId()`, and `MmGetSessionIdEx()` expose basic session queries.
- `MiSessionLeader()` marks a process as the single session leader under the expansion lock.
- `MiSessionCreateInternal()` allocates a session ID, session data pages, session page-directory page, session tag pages, page-table tracking array on 32-bit builds, and initializes `MM_SESSION_SPACE`.
- `MiSessionInitializeWorkingSetList()` maps and initializes `MiSessionSpaceWs`, assigns session working-set limits, and inserts the session into global working-set lists.
- `MmSessionCreate()` promotes the caller to session leader if needed, creates session space, initializes the working set, and marks the process in-session.
- `MiSessionAddProcess()` adds a new process to the current session and increments session references.
- `MiSessionRemoveProcess()`, `MiDereferenceSession()`, `MiDereferenceSessionFinal()`, and `MiReleaseProcessReferenceToSessionDataPage()` remove process/session references and free session data mappings when the last reference is gone.
- `MmSessionDelete()` lets the session leader drop the leader reference.
- `MmAttachSession()` and `MmDetachSession()` attach to the process backing a target session while maintaining an attach count and delete-pending wait event.
- `MmGetSessionById()` scans the session working-set list and returns a referenced process from the requested session.
- `MmQuitNextSession()` releases the process reference obtained by session iteration.

Important state:
- `MmSessionSpace` is the currently mapped per-process session-space pointer.
- `MiSessionDataPages`, `MiSessionTagPages`, `MiSessionTagSizePages`, `MiSessionBigPoolPages`, and `MiSessionCreateCharge` describe per-session page costs.
- `MiSessionIdBitmap` tracks allocated session IDs.
- `MiSessionLeaderExists` enforces a single session leader in this implementation.
- `MiSessionWsList` and `MmWorkingSetExpansionHead` track session working sets.
- `MmExpansionLock` / `MiAcquireExpansionLock()` protect session lists and attach/delete counters.

Important dependencies:
- PFN and PTE allocation primitives: `MiReserveSystemPtes`, `MiRemoveZeroPageSafe`, `MiRemoveAnyPage`, `MiInitializePfnForOtherProcess`, `MiInitializePfnAndMakePteValid`, `MiReleaseSystemPtes`.
- Session view-map initialization from `section.c`: `MiInitializeSystemSpaceMap()`.
- Process flags and process/session links: `PSF_PROCESS_IN_SESSION_BIT`, `PSF_SESSION_CREATION_UNDERWAY_BIT`, `SessionProcessLinks`.
- Kernel attach and synchronization APIs: `KeStackAttachProcess`, `KeUnstackDetachProcess`, guarded mutexes, events, and interlocked counters.

Notable behavior and risks:
- The implementation effectively supports a single session leader globally through `MiSessionLeaderExists`; bitmap expansion for additional session IDs is explicitly not implemented.
- `MiSessionCreateInternal()` has incomplete cleanup on failure. If no session ID is available, it returns while still holding `MiSessionIdMutex` and without clearing `PSF_SESSION_CREATION_UNDERWAY_BIT`.
- Many allocation failures are handled by assertions rather than unwind paths, including page-table and system-PTE allocation.
- Session pool initialization is commented out, so only the data/tag page setup and system-view map are initialized here.
- `MmSessionDelete()` does not reset `MiSessionLeaderExists`, so leader reuse after deletion is not represented in this file.
- `MmGetSessionById()` returns a referenced `EPROCESS`, not an `MM_SESSION_SPACE`, despite its name.
- Several teardown paths flush TLBs or rely on commented-out PDE clearing, showing the session teardown implementation is incomplete.

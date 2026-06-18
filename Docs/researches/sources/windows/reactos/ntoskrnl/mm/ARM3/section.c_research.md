# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/section.c

Read status: complete file, 3587 lines.

This file implements ARM3 section-object support for ReactOS: section protection conversion, pagefile-backed section creation, prototype-PTE setup, process VAD insertion/removal, system/session-space section views, and the `NtCreateSection` / `NtMapViewOfSection` / `NtUnmapViewOfSection` syscall surface. It also bridges some calls to the older ReactOS memory manager for legacy section objects.

Key entry points:
- `MiMakeProtectionMask()` converts Win32 `PAGE_*` protection bits into internal MM protection masks, including guard, no-cache, and write-combine validation.
- `MiInitializeSystemSpaceMap()`, `MiInsertInSystemSpace()`, `MiRemoveFromSystemSpace()`, and `MiUnmapViewInSystemSpace()` manage system/session view address allocation through a bitmap plus hash table.
- `MiFillSystemPageDirectory()` and `MiSessionCommitPageTables()` allocate page tables needed for system or session mappings.
- `MiCreatePagingFileMap()` creates pagefile-backed `SEGMENT`, `CONTROL_AREA`, `SUBSECTION`, and prototype PTE state.
- `MiMapViewOfDataSection()` maps a pagefile-backed section into a process by building an `MMVAD_LONG`, optionally committing prototype PTEs, charging process quota, and inserting the VAD.
- `MiRemoveMappedView()`, `MiUnmapViewOfSection()`, and `MiRemoveMappedPtes()` tear down user, system, and session mappings and drop control-area references.
- `MmCreateArm3Section()` builds ARM3 section objects, currently with a working pagefile-backed path and largely unimplemented file-backed/image paths.
- `MmMapViewOfArm3Section()` validates map parameters and delegates to `MiMapViewOfDataSection()`.
- `MmMapViewInSessionSpace()`, `MmUnmapViewInSessionSpace()`, `MmUnmapViewInSystemSpace()`, and `MmCommitSessionMappedView()` expose kernel/session view operations.
- `NtCreateSection()`, `NtOpenSection()`, `NtMapViewOfSection()`, `NtUnmapViewOfSection()`, `NtExtendSection()`, and `NtAreMappedFilesTheSame()` provide syscall wrappers and probing.
- `MmGetFileObjectForSection()`, `MmGetFileNameForSection()`, `MmGetFileNameForAddress()`, and `MiQueryMemorySectionName()` support image/section filename queries.

Important state:
- `MmMakeSectionAccess[]` and `MmMakeFileAccess[]` map protection masks to section/file access rights.
- `MmUserProtectionToMask1[]`, `MmUserProtectionToMask2[]`, and `MmCompatibleProtectionMask[]` encode protection compatibility.
- `MmSession` is the pseudo-session used for global system-space views.
- `MmSectionCommitMutex` serializes prototype-PTE commitment.
- `MmSectionBasedRoot`, `MmSectionBasedMutex`, and `MmHighSectionBase` support `SEC_BASED` section address selection.

Important dependencies:
- ARM3 PFN/PTE primitives: `MiAcquirePfnLock`, `MiInitializePfnForOtherProcess`, `MiInitializePfnAndMakePteValid`, `MiDeleteVirtualAddresses`, `MI_WRITE_INVALID_PTE`, `MI_WRITE_VALID_PDE`.
- VAD helpers: `MiInsertVadEx`, `MiLocateVad`, `MiLocateAddress`, `MiRemoveNode`, `MiCheckSecuredVad`.
- Object and process APIs: `ObCreateObject`, `ObInsertObject`, `ObReferenceObjectByHandle`, `PsChargeProcessNonPagedPoolQuota`, `KeStackAttachProcess`.
- ReactOS legacy MM compatibility: `MiIsRosSectionObject`, `MiRosUnmapViewOfSection`, `MiRosUnmapViewInSystemSpace`, `MmLocateMemoryAreaByAddress`.

Notable behavior and risks:
- ARM3 section support is deliberately narrow: image sections, file-backed data sections, ROM/global-only-per-session sections, large pages, physical-memory sections, write-watch, and `MEM_RESERVE` mappings are asserted or rejected in many paths.
- `MiCreateDataFileMap()` is a stub that asserts false and returns `STATUS_NOT_IMPLEMENTED`, so the apparent file-backed section path in `MmCreateArm3Section()` cannot complete normally.
- `MiCreatePagingFileMap()` appears to free the `Segment` output parameter rather than `NewSegment` on control-area allocation failure.
- `MiQueryMemorySectionName()` references the target process handle but does not attach to that process before resolving `BaseAddress`; the lookup uses the current address space.
- `MmCommitSessionMappedView()` rejects `LastProtoPte` when it equals the subsection end, although the loop treats it as one-past-end.
- `NtExtendSection()` calls `MmExtendSection()` and may copy back the size, but returns `STATUS_NOT_IMPLEMENTED` unconditionally.
- Several failure paths are intentionally guarded by `ASSERT(FALSE)` rather than recoverable cleanup, matching an incomplete ARM3 implementation stage.

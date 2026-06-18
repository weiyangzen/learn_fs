# File Research: sources/windows/windows-driver-samples/filesys/fastfat/create.c

## Purpose
Implements FastFAT `IRP_MJ_CREATE` handling: opening volumes, root directories, existing files/directories, target directories, and creating or superseding FAT files/directories. This is the central create/open state machine for the sample FAT filesystem driver.

## Main Entry Points
- `FatFsdCreate`: FSD dispatch wrapper. It handles FSDO short-circuit success, enters filesystem context, creates an IRP context, optionally switches to a larger kernel stack on newer NTDDI builds, calls `FatCommonCreate`, and completes or exception-processes the IRP.
- `FatCommonCreate`: core parser and dispatcher for create/open requests. It decodes create options, validates access/disposition combinations, acquires the VCB exclusively, verifies volume and path state, walks cached FCB/DCB prefixes, performs on-disk directory lookup, and routes to the specific open/create helper.
- `FatCommonCreateOnNewStack` / `FatCommonCreateCallout`: Windows threshold-era stack expansion wrappers because create processing consumes significant stack.

## Create/Open Flow
`FatCommonCreate` performs these major phases:
1. Normalizes pathological leading double backslashes and captures create parameters from the IRP stack.
2. Rejects unsupported or invalid requests such as `FILE_OPEN_BY_FILE_ID`, invalid allocation high parts, and simultaneous directory/non-directory constraints.
3. Acquires the VCB exclusively and verifies the volume. Locked, write-protected, EA-on-FAT32, volume-open, root-open, relative-open, and target-directory cases are separated early.
4. Walks the in-memory FCB/DCB tree using OEM short-name lookup first, then Unicode lookup when needed. It validates component length, embedded slash form, trailing slash semantics, delete-pending state, paging-file constraints, and system-file access.
5. If the complete path is cached, opens the existing FCB/DCB without disk lookup.
6. If only a prefix is cached, it walks the remaining path through directory entries, creates missing intermediate DCBs for found subdirectories, and then either opens an existing dirent or creates a new final object.
7. Performs cleanup in layered `try/finally` blocks: unpins BCBs, unwinds partially-created DCB/FCB state, releases the VCB, backs out atomic oplocks on failures, and updates create statistics.

## Existing Object Helpers
- `FatOpenVolume`: opens the volume for direct access. It enforces `FILE_OPEN`/`FILE_OPEN_IF`, may lock the volume depending on share access, flushes/purges referenced file objects, marks clean volumes clean, checks direct-access share state, creates a CCB, sets `FO_NO_INTERMEDIATE_BUFFERING`, and records explicit device access privilege in the CCB.
- `FatOpenRootDcb`: opens the root directory with access/share checks and count updates.
- `FatOpenExistingDcb`: opens an already-cached directory. It handles root delete-on-close denial, EA knowledge checks, access/share checks, Win8+ handle-oplock breaking, atomic create-with-oplock semantics, delete-on-close CCB flagging, and short-name-open tracking.
- `FatOpenExistingFcb`: opens an already-cached file. It handles batch oplocks, implied access for supersede/overwrite, access checks, read-only delete denial, hidden/system overwrite rules, write protection, share/access checks, noncached cache purge optimization, simple opens, and supersede/overwrite routing.
- `FatOpenExistingDirectory`: creates a DCB for an on-disk directory not already cached, then applies access/share/oplock/EA checks and count setup.
- `FatOpenExistingFile`: creates an FCB for an on-disk file not already cached, initializes file size/allocation metadata, optionally looks up paging-file allocation, then performs open or supersede/overwrite.

## New Object Creation
- `FatCreateNewDirectory`: selects short/LFN names, allocates directory entries, handles LFN spans across page boundaries, constructs the short dirent, creates the DCB, performs Win8+ oplock checks including parent-directory advisory break, creates EA metadata where supported, initializes `.`/`..` directory contents, reports directory-added notification, sets share/access counts, and performs extensive rollback if any step fails.
- `FatCreateNewFile`: similar to directory creation but for files. It also uses the tunnel cache to restore short/long names and creation time after delete/recreate patterns, adds initial allocation, marks temporary files, initializes full name metadata, reports file-added notification, sets delete-on-close and manage-volume-access CCB flags, and rolls back allocation, dirents, FCBs, CCBs, and pinned BCBs on abnormal termination.

## Supersede/Overwrite
`FatSupersedeOrOverwriteFile` handles `FILE_SUPERSEDE`, `FILE_OVERWRITE`, and `FILE_OVERWRITE_IF`:
- Rejects EA writes when caller lacks EA knowledge.
- Ensures the file can be truncated despite mappings.
- Creates the file object/CCB and purges cache sections under `VCB_STATE_FLAG_CREATE_IN_PROGRESS`.
- Creates replacement EA metadata before destructive changes.
- Breaks parent directory oplocks on Win8+.
- Truncates file size and allocation, then adds requested allocation.
- Updates dirent size, attributes, timestamps, access date, EA handle, FCB flags, and change notifications.
- Returns `FILE_SUPERSEDED` or `FILE_OVERWRITTEN`.

## Security, Sharing, and Oplocks
The file centralizes several Windows filesystem contract details:
- `FatCheckSystemSecurityAccess` grants `ACCESS_SYSTEM_SECURITY` only when `SE_SECURITY_PRIVILEGE` is held.
- `FatCheckShareAccess` wraps `IoCheckShareAccess` and, on Vista+, rejects opens without write sharing when writable user sections exist.
- Create-with-oplock and oplock-key handling are version-gated across Win7/Win8 paths.
- Sharing failures may trigger handle oplock breaks unless `FILE_COMPLETE_IF_OPLOCKED` is set.

## Important State and Side Effects
- Updates FCB/DCB/VCB open counts, unclean counts, noncached counts, read-only counts, direct-access counts, and share access structures.
- Sets `FO_CACHE_SUPPORTED`, `FO_NO_INTERMEDIATE_BUFFERING`, and `FO_FILE_FAST_IO_READ` depending on create outcome.
- Disables media eject for paging files on removable media.
- Maintains full file names, short-name-open markers, delete-on-close markers, manage-volume-access markers, EA modification count, and notifications.
- Uses BCB pin/unpin and repinned BCB unwind paths heavily; error recovery is a major part of the implementation.

## Research Notes
This file is a dense example of Windows filesystem create semantics layered over FAT constraints: DOS/OEM names, long filename dirents, EA compatibility, tunnel cache behavior, volume locking, oplocks, cache coherency, paging-file special cases, and robust rollback for partially-created on-disk metadata.

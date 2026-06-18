# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/dirtree.cpp

## Purpose

`udf_info/dirtree.cpp` implements UDF directory indexing, name hashing/search, directory packing/retagging, file-entry location caching, and linked/parallel `UDF_FILE_INFO` chain helpers.

## Directory Index Storage

- `UDFDirIndexAlloc()` allocates a frame-based directory index header plus one or more item frames.
- `UDFDirIndexFree()` releases all frames and the header.
- `UDFDirIndexGrow()` extends the last frame or appends a frame.
- `UDFDirIndexTrunc()` shrinks the directory index, preserving residual entries.
- `UDFDirIndex()` returns an item pointer by logical index, with x86 optimized and generic implementations.
- `UDFDirIndexGetFrame()`, `UDFDirIndexInitScan()`, and `UDFDirIndexScan()` support efficient sequential scans across frames.

## Hashing And Names

- `UDFBuildHashEntry()` computes directory lookup hashes:
  - POSIX/case-sensitive hash from the original UTF-16 name
  - uppercase long-name hash
  - DOS 8.3 hash generated through `UDFDOSName()`
- It marks names with `UDF_FI_FLAG_DOS` when the DOS form equals the original name.
- `UDFFindFile()` uses these hashes to search a directory:
  - exact case-sensitive matching when possible
  - fallback case-insensitive long-name matching
  - fallback DOS 8.3 alias matching for names that can be 8.3
  - optional deleted-entry filtering

## Directory Indexing

`UDFIndexDirectory()` builds an in-memory index from a directory extent:

- validates `FileInfo`
- reads the full directory extent into memory
- first scans to count `FILE_IDENT_DESC` entries
- allocates a directory index large enough for entries plus the synthetic self entry
- creates index entry `0` for `.`
- parses each file identifier:
  - computes aligned descriptor length
  - records deleted count
  - creates `..` for `FILE_PARENT`
  - decompresses and normalizes UDF Unicode names for normal entries
  - marks metadata/internal names
  - stores file-entry location, characteristics, offset, length, hashes, and file-info links
- under allocation checking, marks invalid/discarded referenced file-entry blocks as deleted
- stores the finished index in `FileInfo->Dloc->DirIndex`

## Directory Rewrite Helpers

When write support is enabled:

- `UDFPackDirectory__()` removes deleted entries and compacts directory data when `UDF_PACK_DIRS` is enabled.
  - reads valid entries
  - adjusts implementation-use padding so following tags remain block-safe
  - rewrites entries with corrected tags
  - updates `DirIndex` offsets, lengths, and associated `FileInfo` indexes
  - truncates the directory file to the new EOF
- `UDFReTagDirectory()` rewrites descriptor tags for all directory entries when the in-ICB/non-in-ICB data-location state changes.

## File Entry Location Cache

The file manages a VCB-level cache mapping file-entry LBAs to shared `UDF_DATALOC_INFO` objects:

- `UDFFindDloc()` finds a cached Dloc by LBA.
- `UDFFindDlocInMem()` finds the cache slot for a Dloc pointer.
- `UDFFindFreeDloc()` initializes/grows the Dloc cache and returns a free slot.
- `UDFAcquireDloc()` / `UDFReleaseDloc()` set and clear `UDF_FE_FLAG_UNDER_INIT`.
- `UDFStoreDloc()` attaches an existing or newly allocated Dloc to a `UDF_FILE_INFO`.
- `UDFRemoveDloc()` removes and frees a Dloc.
- `UDFUnlinkDloc()` removes a Dloc from the cache without freeing it.
- `UDFFreeDloc()` removes if cached, then frees.
- `UDFRelocateDloc()` updates the cached LBA after relocation.
- `UDFReleaseDlocList()` frees the entire VCB Dloc cache.

## Linked/Parallel FileInfo Helpers

- `UDFGetDirIndexByFileInfo()` returns the parent directory index for a file, excluding stream directories.
- `UDFLocateParallelFI()` finds a linked `FileInfo` with the same parent and directory index.
- `UDFLocateAnyParallelFI()` finds any parallel linked `FileInfo` with the same parent Dloc and index.
- `UDFInsertLinkedFile()` inserts a `FileInfo` into a circular linked chain.

## Integration

This file sits between raw on-disk descriptors from `ecma_167.h`, extent IO helpers, Unicode/name support, FCB/FileInfo lifecycle code, and allocation validation. Its directory index is the basis for path lookup, enumeration, deleted-entry cleanup, and shared hard-link-ish Dloc reuse.

## Notable Risks

- `UDFIndexDirectory()` reads the entire directory extent into memory, so very large directories depend on allocation limits and nonpaged/paged pool availability.
- Recovery from malformed descriptors is limited; utility builds can search for the next plausible file identifier, but normal corruption often returns `STATUS_FILE_CORRUPT_ERROR`.
- Dloc initialization uses a sharing-paused flag; callers must handle `STATUS_SHARING_PAUSED`.
- The code comments note multiply linked objects are not fully supported elsewhere, and this file’s linked/parallel `FileInfo` helpers are a partial cache-sharing mechanism rather than a complete hard-link model.

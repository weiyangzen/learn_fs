# File Research: sources/windows/dokany/dokan/directory.c

Directory enumeration implementation, converting user `WIN32_FIND_DATAW` entries into the Windows directory information classes requested by the kernel.

Key responsibilities:
- Defines `DOKAN_FIND_DATA`, the internal wrapper for `WIN32_FIND_DATAW` entries.
- Provides fill helpers for:
  - `FileDirectoryInformation`
  - `FileFullDirectoryInformation`
  - `FileIdFullDirectoryInformation`
  - `FileNamesInformation`
  - `FileBothDirectoryInformation`
  - `FileIdBothDirectoryInformation`
  - `FileIdExtdDirectoryInformation`
  - `FileIdExtdBothDirectoryInformation`
- Aligns directory entries to 8-byte boundaries with `QuadAlign`.
- Implements `DokanFillFileData()` callback to append user-provided `WIN32_FIND_DATAW` entries to a `DOKAN_VECTOR`.
- Implements `MatchFiles()` to filter cached entries by search pattern, file index, single-entry requests, and buffer capacity.
- Adds missing `.` and `..` entries for non-root wildcard directory scans.
- Caches enumeration results and search pattern per `DOKAN_OPEN_INFO`.
- Dispatches `FindFilesWithPattern` first, falls back to `FindFiles`, and filters internally when pattern-aware enumeration is unavailable.
- Implements `DokanIsNameInExpression()` for Windows-style wildcard matching, including DOS wildcard characters `<`, `>`, and `"`.

Important behavior:
- Reuses cached directory lists unless the search pattern changes or `SL_RESTART_SCAN` requires a rescan.
- `SL_INDEX_SPECIFIED` overrides restart behavior to match FastFat semantics.
- Returns `STATUS_NO_SUCH_FILE` for no match at index 0, `STATUS_NO_MORE_FILES` after prior entries, and `STATUS_BUFFER_OVERFLOW` when the output buffer is too small.
- Directory entries set `NextEntryOffset` except for the last returned entry.
- Case sensitivity follows `DOKAN_OPTION_CASE_SENSITIVE`.

Dependencies:
- Uses `DOKAN_VECTOR` for directory-list storage.
- Uses pooled directory lists and temporary open info from `dokan_pool.c`.
- Uses user callbacks `FindFilesWithPattern` and `FindFiles`.
- Uses `ALIGN_ALLOCATION_SIZE()` from `dokan.c` to report allocation size consistently with volume options.

Notable risks:
- `DokanFillFileData()` does not check `DokanVector_PushBack()` failure, so out-of-memory during enumeration is not propagated.
- `MatchFiles()` writes `NextEntryOffset` through `PFILE_BOTH_DIR_INFORMATION` even when the actual information class differs; this relies on compatible leading layout.
- The temporary open-info path for events without open context can cache during the dispatch but is immediately returned to the pool after completion.
- The wildcard matcher is recursive for `*` and DOS star matching, so pathological patterns/names can be expensive.

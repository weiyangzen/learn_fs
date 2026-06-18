# sources/user-network-fs/samba/source4/torture/raw/search.c

## Purpose
This file implements the raw SMB search torture suite. It validates old SMB search levels and TRANS2 find levels for single-file metadata consistency, multi-page enumeration continuation, directory modification during search, ordering behavior, concurrent old-style search handles, OS/2-style delete while enumerating, EA-list search semantics, and `max_count` behavior.

## Important APIs, Types, And Functions
The exported helper `torture_single_search()` performs one-entry searches across `RAW_SEARCH_SEARCH`, `RAW_SEARCH_FFIRST`, `RAW_SEARCH_FUNIQUE`, and `RAW_SEARCH_TRANS2`. The static `levels[]` table maps search level/data-level pairs to names, name offsets, resume-key offsets, capabilities, and stored results. `extract_name()` and `extract_resume_key()` use those offsets to interpret `union smb_search_data` generically.

`setup_smb1_posix()` negotiates SMB1 POSIX extensions for `RAW_SEARCH_DATA_UNIX_INFO`. `multiple_search()` performs find-first/find-next loops using continuation by flags, last name, or resume key. `multiple_search_callback()` accumulates results in `struct multiple_result`. Test entry points are registered by `torture_raw_search()`.

## Control Flow
`test_one_file()` creates `torture_search.txt`, queries every search level, checks the not-found status for a missing file, fetches file-info levels, and compares search metadata with pathinfo metadata: attributes, times, sizes, allocation, EA size, alternate names, long names, Unix names, and file IDs.

`test_many_files()` creates 700 files and enumerates them across many data levels and continuation modes, then sorts returned names and verifies the complete expected set. `test_modify_search()` starts an enumeration, mutates the directory by adding, deleting, hiding, system-marking, and delete-on-close-marking files, then checks which names should appear. `test_sorted()` observes whether the server naturally returns alphabetically sorted names but treats unsorted output as informational rather than a failure.

`test_many_dirs()` exercises old-style search IDs across 20 directories and checks search-next behavior including rewind support. `test_os2_delete()` enumerates with EA-size records and deletes files while continuing by resume key until all files are gone. `test_ea_list()` creates files with EAs, queries selected EA names through `RAW_SEARCH_DATA_EA_LIST`, continues the search, sorts results, and validates returned EA names and values. `test_max_count()` confirms that TRANS2 find-first with `max_count = 0` returns one entry and a following find-next with `max_count = 1` returns one more.

## State And Persistence Behavior
Most tests operate under `\testsearch` and remove it with `smbcli_deltree()`. They create hundreds of files/directories, set attributes, set EAs, mark delete-on-close, and hold server-side search handles until close-on-end flags or session exit. The module uses static `levels[]` result storage and a static `compare_data_level` for sorting callbacks.

## Dependencies And Integration Points
The file depends on raw search APIs (`smb_raw_search_first`, `smb_raw_search_next`, `smb_raw_search_close`), raw path/file info, raw setpathinfo, Unix extension negotiation through TRANS2, talloc, type-safe sorting, and torture settings including `resume_key_support`, `rewind_support`, `raw_search_search`, `search_ea_size`, `search_ea_support`, and `ea_support`. It is registered as the nested raw `search` suite.

## Risks And Edge Cases
Search semantics vary across servers, especially resume keys, ordering, old search rewind, POSIX/Unix info, and EA support. Some tests deliberately skip based on settings or warn on unsupported levels. Directory mutation during enumeration is inherently compatibility-sensitive. Generic offset extraction is compact but fragile if `union smb_search_data` layout changes without updating `levels[]`.

## Test Signals
Success signals include exact metadata parity with `ALL_INFO`, complete enumeration of 700 files under multiple continuation mechanisms, correct inclusion/exclusion after directory mutation, expected behavior for old-style search handles, full deletion count during OS/2-style delete, exact EA-list values, and correct `max_count` handling. Failures include level names, expected statuses, field-level mismatches, missing/extra names, and count discrepancies.

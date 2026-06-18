# sources/user-network-fs/samba/source4/torture/raw/lookuprate.c

## Purpose
`lookuprate.c` implements `torture_bench_lookup()`, a benchmark/regression test for missing-name lookup scalability. It verifies that lookup rates for a non-existent path remain roughly constant as the containing directory grows from empty to large entry counts.

## Important APIs, Types, and Functions
- `struct rate_record records[]` defines directory sizes and stores measured `TRANS2_QUERY_PATH_INFORMATION` and `TRANS2_FIND_FIRST2` rates.
- `fill_directory()` creates the test directory and fills it with randomly named files.
- `querypath_lookup()` calls `smbcli_qpathinfo()`, while `findfirst_lookup()` calls `smbcli_list()`.
- `squash_lookup_error()` treats expected missing-file/path statuses as success.
- `lookup_rate_convert()` loops for two seconds and converts operation count into lookups per second.
- `remove_working_directory()` retries `smbcli_deltree()` up to five times for very large directories.

## Control Flow
The test opens one SMB connection, removes any prior `\\lookuprate`, then iterates through the configured record sizes. For each size it creates and fills the directory, measures missing `\\lookuprate\\foo` lookup rate with query-path and find-first methods, prints the rates, and deletes the directory. After all samples it compares every sample to the empty-directory baseline using a ten-percent fuzz threshold.

## State and Persistence Behavior
Measurements are stored in the static `records[]` array for the life of the process. Server-side state is the temporary `\\lookuprate` tree and generated filler files, removed between each sample and again at exit.

## Dependencies and Integration Points
The benchmark uses `torture_open_connection`, classic `smbcli_*` helper APIs, timeval helpers, and `torture/raw/proto.h`. It exercises server directory lookup/indexing behavior through normal SMB path and search operations.

## Risks and Edge Cases
- The largest sample creates 100,000 files; this is expensive and cleanup can fail on some servers.
- The ten-percent threshold can be too strict on noisy networks or cold caches.
- `random()` names are not seeded here, so reproducibility depends on process state.
- `usec_to_sec()` truncates integer microseconds before double division, reducing precision for short periods, though the loop runs for about two seconds.

## Test Signals
Signals are fill rates, measured querypath/findfirst lookups per second, failure statuses from fill or lookup, cleanup retry messages, and final deviations beyond `FUZZ_PERCENT`.

# sources/user-network-fs/samba/source4/torture/smb2/timestamps.c

## Purpose
`timestamps.c` implements SMB2 timestamp torture suites. It validates timestamp round-tripping across extreme `time_t` values, special `NTTIME_FREEZE` and `NTTIME_THAW` values, close response behavior, immediate write-time update rules, sticky write-time semantics across multiple handles, EOF/allocation-size metadata effects, and a Windows timestamp-resolution observation test.

## Important APIs, Types, and Functions
The main suite entry points are `torture_smb2_timestamps_init()` and `torture_smb2_timestamp_resolution_init()`. Registered tests include `test_close_not_attrib`, many `time_t_*` cases, `freeze-thaw`, delayed write-time tests, two multi-tree `modern_write_time_update` tests, and `resolution1`.

Key helpers are `test_time_t()`, which sets create/write times and verifies both handle getinfo and directory find results, `test_delayed_write_vs_setbasic_do()`, which reuses a caller-provided basic-info setinfo payload, and `getinfo_both()`, which compares handle-based and path-based write times. The code uses `struct smb2_create`, `struct smb2_close`, `struct smb2_find`, `struct smb2_flush`, `union smb_fileinfo`, `union smb_setfileinfo`, `NTTIME`, `unix_to_nt_time()`, and `full_timespec_to_nt_time()`.

## Control Flow
Each test cleans `smb2-timestamps`, creates a test directory, creates or opens `testfile.dat` or a generated filename, and performs SMB2 create, setinfo, getinfo, write, flush, close, and find requests. `test_close_no_attrib()` closes without full-information flags and asserts that close output attributes and times are omitted. `test_time_t()` covers future, epoch, negative, and pre-1970 values by setting basic information, verifying direct getinfo, verifying `SMB2_FIND_ID_BOTH_DIRECTORY_INFO`, reopening, and verifying again.

`test_freeze_thaw()` sets known timestamps, then submits `NTTIME_FREEZE` and `NTTIME_THAW` and verifies neither changes stored values. `test_delayed_write_vs_seteof()`, `test_delayed_write_vs_flush()`, `test_delayed_write_vs_setbasic()`, `test_delayed_1write()`, and `test_delayed_2write()` check modern immediate write-time behavior, including that flush and close do not apply extra pending write-time changes and that explicit write-time setinfo is respected.

`test_modern_write_time_update1()` opens the same file from two SMB2 trees and verifies that writes and sticky write-time settings are visible consistently through both handles and path opens. It confirms that after a handle sets a sticky future write time, writes from that same handle preserve it, while a write from the second handle unfreezes and advances it. `test_modern_write_time_update2()` applies the same multi-handle model to end-of-file and allocation-size updates, distinguishing mtime and ctime behavior. `test_timestamp_resolution1()` documents Windows 2019-style roughly 15 ms resolution: an immediate write may not change close write time, while a write after 20 ms should.

## State and Persistence Behavior
The tests create and remove the `smb2-timestamps` tree. Server state under test is file timestamps, close response fields, write-time sticky state, allocation size, EOF size, change time, open handles across two tree connections, and directory search metadata. Several tests intentionally sleep or wait milliseconds to avoid filesystem timestamp granularity.

## Dependencies and Integration Points
The file depends on SMB2 client calls, SMB2 torture helpers, general torture assertions, `torture/util.h`, time conversion utilities, and generated SMB2 suite prototypes. The two modern update tests are registered as `torture_suite_add_2smb2_test()` because they require two SMB2 tree connections.

## Risks
Timestamp tests are inherently sensitive to server clock behavior, filesystem resolution, network latency, and platform time range support. Extreme negative and far-future values may expose backend limitations. The resolution test is explicitly timing-dependent and documented as unsuitable for normal Samba CI.

## Test Signals
Signals include exact `NTTIME` equality or inequality checks, directory find metadata matching handle metadata, close output fields being omitted or preserved as expected, mtime/ctime changes after EOF and allocation operations, sticky write-time preservation, and consistent values observed through concurrent handles and path opens.

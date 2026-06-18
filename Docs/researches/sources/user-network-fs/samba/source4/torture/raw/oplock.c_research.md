# sources/user-network-fs/samba/source4/torture/raw/oplock.c

## Purpose
This file implements the raw SMB oplock torture suite, an oplock benchmark, and a manual oplock-hold tool. It validates exclusive, level-II, and batch oplock behavior across conflicting opens, share modes, deletes, renames, path/file information updates, byte-range locks, alternate data streams, delete-on-close, clients without level-II support, and timeout paths. The registered `raw.oplock` suite is a dense compatibility baseline for how Samba and Windows servers should grant, break, downgrade, acknowledge, or time out oplocks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_oplock()`, which registers two-connection tests `exclusive1` through `exclusive9`, `level_ii_1`, `batch1` through `batch26`, `stream1`, `doc1`, `brl1`, `brl4`, and one-connection tests `brl2` and `brl3`. Additional exported entry points are `test_trans2rename()`, `test_nttransrename()`, `torture_bench_oplock()`, and `torture_hold_oplock()`.

Global `break_info` records the last break fnum, break level, count, and failures. Oplock handlers include `oplock_handler_ack_to_given()`, `oplock_handler_ack_to_none()`, `oplock_handler_timeout()`, `oplock_handler_close()`, and `oplock_handler_hold()`. Support helpers include `open_connection_no_level2_oplocks()`, `timeout_cb()`, `torture_wait_for_oplock_break()`, `get_break_level1_to_none_count()`, and `get_setinfo_break_count()`. Key APIs are `smbcli_oplock_handler()`, `smbcli_oplock_ack()`, `smb_raw_open()`, `smb_raw_close_send()`, `smb_raw_unlink()`, `smb_raw_rename()`, `smb_raw_setpathinfo()`, `smb_raw_setfileinfo()`, `smb_raw_pathinfo()`, `smb_raw_fileinfo()`, `smbcli_lock()`, `smbcli_write()`, and `tevent_loop_once()`.

## Control flow
The test functions share a common scaffold: set up `\test_oplock`, unlink test files, install oplock handlers on one or more transports, issue `RAW_OPEN_NTCREATEX` requests with oplock request flags, perform a second operation that may contend with the cached handle, run `torture_wait_for_oplock_break()`, and compare `break_info` plus returned oplock levels and statuses.

The exclusive tests cover share-none versus share-all behavior, second opens that should or should not break, unlink/rename behavior, `setpathinfo` EOF and rename updates, attribute-only opens, delete-access opens, create-disposition-specific break levels, and conversion from exclusive to level-II. The level-II test specifically verifies that an unacknowledged break to none happens once and that later writes do not generate duplicate breaks.

The batch tests cover the broadest surface. They verify unlink and open contention, handler choices that ack to none or close the file, self reads and writes, attribute-only opens, second and third level-II opens, set EOF/allocation updates, `qpathinfo`, ordinary rename and NT rename, setfileinfo/setpathinfo rename, delete-on-close behavior, client support for level-II oplocks, timeout timing, and path attribute updates that should not break. Target-specific branches encode known Windows and Samba differences for XP, Windows Server 2003/2008/2012, Samba3, and Samba4.

Specialized tests include `test_raw_oplock_stream1()`, which is skipped for Samba3/4 and checks named stream/default stream oplock grant and break behavior; `test_raw_oplock_doc()`, which expects a second open to return `DELETE_PENDING` without an oplock break after delete-on-close; and BRL tests that exercise interaction between batch/exclusive oplocks and byte-range lock acquisition with one handle, two handles on one connection, and two clients.

`torture_bench_oplock()` opens a configurable number of connections, installs a close-on-break handler, and repeatedly opens the same file with a batch oplock from each connection for a configured time limit to measure and stress oplock handoff. `torture_hold_oplock()` opens four files with different share-access and close-on-break behavior, writes one byte to each, then waits in the event loop for manual external oplock experiments.

## State and persistence
Server state is concentrated under `\test_oplock`, plus individual files for each test. The persistent behavior under test includes open-handle state, share-mode state, cached oplock levels, break delivery, break acknowledgements, file rename identity, byte-range lock state, alternate stream state, delete-on-close state, and client capability negotiation. Local process state is mostly `break_info`; the manual hold mode also uses the static `hold_info[]` table to map fnums to close-on-break behavior. Cleanup generally exits sessions and deletes the test tree, but benchmark/manual modes are intentionally long-running or externally driven.

## Dependencies and integration points
The file depends on Samba's raw SMB client API, tevent, command-line credentials, resolver and loadparm configuration, torture target-detection macros (`TARGET_IS_*`), and raw rename tests that call `test_trans2rename()` and `test_nttransrename()` from this file because oplock handling is required. `open_connection_no_level2_oplocks()` exercises client option integration by creating a special connection with `use_level2_oplocks = false`.

## Risks
Oplock tests are timing-sensitive: `torture_wait_for_oplock_break()` waits only about 100 ms for most breaks, while timeout tests rely on the configured server oplock timeout. Slow transports can cause false negatives. `break_info` is global and must be zeroed before each expected event; missing resets would make tests order-dependent. Several branches intentionally encode known server-version quirks, making the suite brittle when target detection is wrong or server behavior changes. Async close from inside a break handler can race with later explicit close calls. The manual hold mode loops indefinitely and leaves files open by design.

## Test signals
Strong signals are wrong `oplock_level` returns (`BATCH_OPLOCK_RETURN`, `EXCLUSIVE_OPLOCK_RETURN`, `LEVEL_II_OPLOCK_RETURN`, `NO_OPLOCK_RETURN`), wrong `break_info.count`, fnum, or break level, unexpected handler failures, wrong status codes (`SHARING_VIOLATION`, `DELETE_PENDING`, `LOCK_NOT_GRANTED`, `OK`), duplicate breaks after timeout, missing rename visibility through fileinfo, and benchmark throughput or handoff failures in `torture_bench_oplock()`.

# File Research: sources/windows/winbtrfs/src/tests/oplock.cpp

## Purpose

This is the WinBtrfs user-mode oplock conformance test file. It exercises legacy oplock FSCTLs and Windows 7+ `FSCTL_REQUEST_OPLOCK` behavior against Btrfs-backed files and directories, checking when oplocks are granted, denied, broken, downgraded, or left intact.

The test entry points are declared in `src/tests/test.h` and registered in `src/tests/test.cpp` as:
- `oplock_i`
- `oplock_ii`
- `oplock_batch`
- `oplock_filter`
- `oplock_r`
- `oplock_rw`
- `oplock_rh`
- `oplock_rwh`

## Main Structure

The file defines local FSCTL constants, oplock level constants, request flags, and an `oplock_type` enum covering:
- legacy level 1, level 2, batch, and filter oplocks
- Windows 7+ read, read-handle, read-write, and read-write-handle oplocks

Helper functions:
- `req_oplock` requests legacy oplocks with `NtFsControlFile` and expects `STATUS_PENDING`.
- `req_oplock_win7` requests modern cache-level oplocks using `REQUEST_OPLOCK_INPUT_BUFFER` / `REQUEST_OPLOCK_OUTPUT_BUFFER`.
- `check_event` queries the notification event state to tell whether the oplock break completed.
- `lock_file_wait` and `unlock_file` wrap byte-range lock operations.
- `ack_oplock` / `ack_oplock_win7` spawn a thread that waits for a break event and acknowledges the break through the matching FSCTL.

## Test Coverage

`test_oplocks_ii` covers level 2 oplocks. It verifies shared readers do not break the oplock, but write/truncation/data-changing operations do. It also checks denial cases such as locked files, synchronous handles, directories for legacy level 2, and incompatible existing oplocks.

`test_oplocks_r` covers modern read oplocks. It checks similar read-sharing behavior, write-triggered break behavior, directory read oplocks on Windows 8+ semantics, compatibility with level 2/read oplocks, and incompatibility with stronger oplocks.

`test_oplocks_i` covers legacy level 1 oplocks. It tests downgrade to level 2 on compatible opens, break-to-none on overwrite/supersede style opens, self-handle operations that should not break, and conflicts with other oplock types.

`test_oplocks_rw` covers read-write oplocks. It checks downgrades to read on reader opens, break-to-none on overwrite/supersede/reserve-filter paths, self-handle operations that remain stable, and upgrade/conflict behavior against read/read-write/read-handle/read-write-handle/legacy oplocks.

`test_oplocks_batch` covers batch oplocks. It tests break-to-level-2 for ordinary opens, break-to-none for destructive opens, stable self-handle metadata/data operations, and incompatibility with most existing oplock types.

`test_oplocks_rwh` covers read-write-handle oplocks. It validates downgrade to read-handle on compatible second opens, break-to-none on destructive opens, stable self-handle operations, and upgrade/conflict behavior with modern and legacy oplocks.

`test_oplocks_filter` covers filter oplocks. It checks that read-only opens can coexist, write opens and destructive opens break the filter oplock, local/self operations stay unbroken, and incompatible existing oplocks prevent granting another filter oplock.

`test_oplocks_rh` covers read-handle oplocks. It checks coexistence with read opens, behavior with `FILE_COMPLETE_IF_OPLOCKED`, destructive-open breaks, directory read-handle oplocks, multiple-handle cases, and compatibility/conflict behavior with other oplock types.

Most scenario groups follow the same pattern:
1. Create or open a test file.
2. Request a specific oplock.
3. Assert the event is initially unsignaled.
4. Perform a second open or file operation.
5. Assert the event and returned break level (`iosb.Information` or `roob.NewOplockLevel`).
6. Reset handles and repeat for the next operation.

## Dependencies And Side Effects

This file depends heavily on helpers from `test.h` and other test files:
- file creation/open wrapper `create_file`
- synchronous read/write helpers
- file information setters for EOF, allocation, valid data length, zero-data, rename, hardlink, and disposition
- privilege adjustment helpers
- `unique_handle`, `ntstatus_error`, `formatted_error`, and `exp_status`

Several tests temporarily enable `SeManageVolumePrivilege` because valid-data-length changes require it, then call `disable_token_privileges(token)` before returning from each public test function.

The tests create many files/directories under the provided test directory, using prefixes such as `oplockii`, `oplockr`, `oplocki`, `oplockrw`, `oplockb`, `oplockrwh`, `oplockf`, and `oplockrh`.

## Notable Observations

The file is a behavioral compatibility suite, not production driver logic. Its value is in encoding expected Windows oplock semantics for WinBtrfs.

There are a few apparent copy/paste quirks in labels or calls:
- In `test_oplocks_filter`, the “Try to get filter oplock with two handles open” scenario calls `req_oplock(..., oplock_type::batch)`.
- In `test_oplocks_rwh` and `test_oplocks_rh`, final test labels mention “batch oplock” while the called modern oplock type is read-write-handle or read-handle.
- Some directory child creation tests pass `FILE_DIRECTORY_FILE` for a path named `file`; this likely creates a child directory despite the test label saying “file”.

These do not change the broad purpose, but they matter if this file is used as ground truth for test names or scenario classification.

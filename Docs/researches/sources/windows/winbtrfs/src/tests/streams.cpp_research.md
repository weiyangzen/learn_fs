# File Research: sources/windows/winbtrfs/src/tests/streams.cpp

## Purpose

`streams.cpp` tests alternate data stream behavior in WinBtrfs. It covers default stream reporting, named stream creation and deletion, streams on directories, stream data I/O, stream renames, conversion between default and named streams, stream naming rules, reserved Btrfs-backed stream names, and case-insensitive stream lookup.

## Main Helper

- `query_streams(HANDLE h)`: repeatedly calls `NtQueryInformationFile(..., FileStreamInformation)`, grows the buffer on `STATUS_BUFFER_OVERFLOW`, and returns copied `FILE_STREAM_INFORMATION` records.

## Behavior Covered

The initial tests create a base file and verify it reports one `::$DATA` stream with zero size/allocation and `FILE_STANDARD_INFORMATION_EX.AlternateStream == false`. Creating `stream1:stream` is expected to use the same file ID as the base file and set `AlternateStream == true`.

The file checks that creating a stream on a nonexistent base path creates the base file. It rejects stream creation with `FILE_DIRECTORY_FILE`, tests directory streams separately, and confirms directory default stream reporting uses an empty stream name rather than `::$DATA`.

Data-path coverage writes to a named stream, reads it back, validates stream size/allocation reporting, calls zero-data operations, truncates via end-of-file, and confirms resulting bytes and metadata.

Disposition coverage distinguishes deleting a stream from deleting the base file. Deleting `stream6:stream` leaves `stream6` visible, while deleting `stream7` removes the base file and its stream. Stream create/open/open-if/overwrite/overwrite-if/supersede dispositions are all exercised.

Rename coverage is detailed. Renaming a stream using a full path is invalid, while a relative stream name such as `:stream2` succeeds. Renaming a named stream to `::$DATA` requires replacement and converts it back to the default stream. Directory stream conversion to `::$DATA` is rejected. A base file can be renamed to a named stream, making the handle report `AlternateStream == true`.

The file validates `::$DATA` and `:$DATA` suffix handling, including case-insensitive `$data`. It also tests opening named streams with explicit `$DATA` type suffixes.

Name validation covers long stream names, emoji names, long UTF-8 emoji sequences, malformed UTF-16 surrogate sequences, unusual characters, and WinBtrfs-reserved stream names such as `DOSATTRIB`, `reparse`, `EA`, and `casesensitive`. As in rename tests, some expected statuses depend on `fstype == fs_type::ntfs`.

The final case confirms case-insensitive lookup across both base filename and stream name by creating `stream16:stream` and opening `STREAM16:STREAM`.

## Integration Points

This file uses shared helpers from `test.cpp` and `test.h`: `create_file`, `query_information`, `write_file`, `write_file_wait`, `read_file`, `read_file_wait`, `set_zero_data`, `set_end_of_file`, `set_disposition_information`, `set_rename_information`, `query_dir`, and global `fstype`.

## Research Notes

This file documents the WinBtrfs mapping between Windows alternate data streams and Btrfs extended metadata/storage. Reserved stream names are particularly important because they collide with internal WinBtrfs metadata streams that NTFS would otherwise allow.

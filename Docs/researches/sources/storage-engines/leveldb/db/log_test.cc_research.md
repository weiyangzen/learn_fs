# sources/storage-engines/leveldb/db/log_test.cc

## Purpose
This gtest suite validates the log writer/reader pair across normal records, fragmentation, block-boundary trailers, append mode, random data, corruption paths, and initial-offset reading.

## Important APIs, Types, And Functions
Helpers generate big/random strings and numbers. `LogTest` owns in-memory `StringDest`, `StringSource`, `ReportCollector`, `Writer`, and `Reader`. It provides `Write`, `Read`, byte mutation/truncation helpers, checksum repair, `ReopenForAppend`, forced read errors, error matching, and initial-offset helpers.

## Control Flow
Tests write records into memory, switch to reading lazily, then assert exact returned logical records or EOF. Corruption tests mutate header bytes, lengths, checksums, record types, or remove fragments and then verify returned records plus dropped-byte/error reports. Initial-offset tests construct a known multi-block log and assert which logical record is returned from many physical offsets.

## State And Persistence Behavior
No disk files are used; the in-memory dest/source models persistent log bytes. The suite validates durable format behavior: block padding, fragmentation, checksum coverage, append with existing file length, and tolerance for truncated final records.

## Dependencies And Integration Points
It depends on `log_reader`, `log_writer`, Env file interfaces, coding, crc32c, random utilities, and gtest. It protects DB recovery and manifest replay behavior.

## Risks And Edge Cases
Expected dropped byte counts are tied to exact block/header math. Some corruption paths intentionally recover later records, while truncated trailing records are ignored to model writer crashes.

## Test Signals
Failures indicate WAL format incompatibility, bad fragment assembly, false corruption reporting, missed corruption, broken append offsets, or incorrect physical-offset resync.

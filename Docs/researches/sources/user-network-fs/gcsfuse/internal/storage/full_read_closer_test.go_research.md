# sources/user-network-fs/gcsfuse/internal/storage/full_read_closer_test.go

## Purpose
This file tests `gcsFullReadCloser` against a deliberately partial reader that returns at most two bytes per `Read` call.

## Important APIs and Control Flow
`twoBytesStorageReader` implements `Read`, `Close`, and `ReadHandle`, using a `bytes.Buffer` while limiting each read to two bytes. `TestFullReaderCloser` runs table-driven parallel subtests for a buffer larger than the data, smaller than the data, and equal to the data. Each case writes data to the fake reader, wraps it with `newGCSFullReadCloser`, reads once, and asserts byte count, error, and output bytes.

## State, Dependencies, and Integration
State is local to each test case via an isolated buffer. Dependencies include `bytes`, `io`, Go `testing`, `cloud.google.com/go/storage`, and `testify/assert`. The test confirms the wrapper preserves `StorageReader` compatibility and fixes short-read behavior.

## Risks and Test Signals
The cases confirm the key invariant: successful reads return exactly the requested buffer length, and short final responses return `io.EOF` rather than `io.ErrUnexpectedEOF`. The fake reader's `ReadHandle` and `Close` are minimal, so delegation behavior is not deeply tested.

# sources/sync-backup/casync/src/canbd.h

## Purpose
`canbd.h` declares the opaque `CaBlockDevice` API for serving casync data through Linux NBD. It lets higher-level code configure, open, poll, inspect, and answer block-device read requests.

## Important APIs, Types, and Functions
The enum return states are `CA_BLOCK_DEVICE_CLOSED`, `CA_BLOCK_DEVICE_REQUEST`, and `CA_BLOCK_DEVICE_POLL`. Public functions cover allocation/unref, size setup, device open, stepping, request offset/size getters, response writing, polling, path and friendly-name configuration, device-number retrieval, poll fd retrieval, and detection of `/dev/nbd*` paths.

## Control Flow
The expected sequence is allocate, configure size/path/name, open, poll/step, answer requests, and unref. The API exposes exactly one outstanding request at a time through `last_request` in the implementation.

## State and Persistence
The type is opaque to callers. State is held in file descriptors, a child process, kernel NBD attachment, and optional `/run/casync` friendly-name metadata.

## Dependencies and Integration Points
The header includes integer, signal, and sys/types definitions. `casync-tool.c` uses it to implement block-device presentation of archives.

## Risks
This API is Linux-specific despite the header not spelling out all kernel requirements. The caller must answer exactly the requested offset and size; `ca_block_device_put_data()` rejects mismatches.

## Test Signals
The shell NBD integration test is the main visible signal. Compile-time coverage comes through the `casync` tool build.

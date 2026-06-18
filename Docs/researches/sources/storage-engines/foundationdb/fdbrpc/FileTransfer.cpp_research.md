# sources/storage-engines/foundationdb/fdbrpc/FileTransfer.cpp

## Purpose
`FileTransfer.cpp` implements a gRPC file-transfer service and client, conditionally compiled when `FLOW_GRPC_ENABLED` is set. It supports metadata lookup, server-streamed chunk downloads, optional CRC32C verification, and test error injection.

## Important APIs, Types, and Functions
Important functions are `crc32_checksum_ifstream`, `FileTransferServiceImpl::DownloadFile`, `FileTransferServiceImpl::GetFileInfo`, `FileTransferClient::GetFileInfo`, and `FileTransferClient::DownloadFile`.

## Control Flow
The service `DownloadFile` opens the requested file at end to determine size, chooses request chunk size or a default, seeks to `first_chunk_index * chunk_size`, then streams `DownloadChunk` messages with offsets and data until EOF. It can randomly fail or flip a byte for testing. `GetFileInfo` returns requested size and/or CRC. The client first fetches expected size and optional CRC, starts the streaming RPC, writes chunks sequentially to the output file, rejects offset gaps/reordering, verifies byte count and CRC, checks final gRPC status, and deletes the output file on failure.

## State and Persistence Behavior
Server state is the `error_inject_` enum and local filesystem contents. Client persistence is the output file, which is truncated on open and removed on failed transfer when `delete_on_close_` is true. No resume metadata is persisted.

## Dependencies and Integration Points
It depends on generated `file_transfer` protobuf/gRPC stubs, gRPC C++ APIs, CRC32C, deterministic randomness, C++ streams, and `FileTransfer.h`. It is built only in gRPC-enabled fdbrpc builds.

## Risks and Edge Cases
The server error text for missing file in `DownloadFile` says "File found not". `DownloadFile` ignores `ServerContext` cancellation. `expected_size` is stored as `uint32_t` even though protobuf file size may exceed 4 GiB. Client download does not set chunk size or resume index, so resume support is absent despite proto fields. CRC verification opens the output file without explicit binary mode. The service trusts requested file paths without path policy.

## Test Signals
`FlowGrpcTests.cpp` includes file transfer success for a 40 MiB file, byte-flip detection through CRC mismatch, and random internal failure handling.

# sources/storage-engines/foundationdb/fdbrpc/protos/file_transfer.proto

## Purpose

`file_transfer.proto` defines the gRPC contract for FoundationDB fdbrpc file transfer support. It supports querying file metadata and streaming file contents in chunks.

## Important APIs, types, and functions

The `fdbrpc.FileTransferService` service has unary `GetFileInfo(GetFileInfoRequest) returns (GetFileInfoReply)` and server-streaming `DownloadFile(DownloadRequest) returns (stream DownloadChunk)` RPCs. `DownloadRequest` carries `file_name`, `chunk_size`, and `first_chunk_index`. `DownloadChunk` carries `offset` and raw `data`. `GetFileInfoRequest` carries `file_name`, `get_size`, and `get_crc_checksum`. `GetFileInfoReply` carries `file_size` and `crc_checksum`.

## Control flow, state, and persistence

The proto has no runtime state itself. Generated stubs drive `FileTransferServiceImpl` and `FileTransferClient`: the server opens the requested file, streams chunks from `first_chunk_index * chunk_size`, and optionally computes size and CRC32C metadata. Persistence is the underlying file on disk, outside the proto contract.

## Dependencies and integration points

`fdbrpc/CMakeLists.txt` runs `generate_grpc_protobuf(fdbrpc.file_transfer protos/file_transfer.proto)` when `WITH_GRPC` is enabled and links `proto_fdbrpc_file_transfer` into `fdbrpc` and `fdbrpc_sampling`. `FileTransfer.h/.cpp` include the generated `file_transfer.pb.h` and `file_transfer.grpc.pb.h`. `FlowGrpcTests.cpp` registers `FileTransferServiceImpl` and tests normal transfer and error-injection paths.

## Risks and test signals

The protocol trusts `file_name` as supplied by the caller; path authorization and sandboxing must be enforced by the service layer or deployment context. `chunk_size` is `int32`; the implementation defaults nonpositive values but large values can drive memory allocation. CRC32C is useful for corruption detection but is not a strong checksum, and the file notes TODOs for stronger or partial checksums. Test signals are generated-code builds with `WITH_GRPC`, gRPC file transfer tests, resume-from-`first_chunk_index` behavior, checksum mismatch detection, and compatibility checks before changing field numbers.

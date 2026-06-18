# sources/storage-engines/foundationdb/fdbrpc/FileTransfer.h

## Purpose
`FileTransfer.h` declares the gRPC file-transfer service implementation and client wrapper for fdbrpc.

## Important APIs, Types, and Functions
`FileTransferServiceImpl` derives from `fdbrpc::FileTransferService::Service` and declares `DownloadFile`, `GetFileInfo`, test `ErrorInjection` modes, and `SetErrorInjection`. `FileTransferClient` owns a generated stub and declares `GetFileInfo` and `DownloadFile`.

## Control Flow
The header does not implement control flow, but it defines unary metadata lookup and server-streamed download as the service surface. The client API wraps these RPCs into optional-returning C++ calls.

## State and Persistence Behavior
The service stores only the selected error-injection mode. The client stores a stub and a constant policy to delete failed output files.

## Dependencies and Integration Points
It is compiled only under `FLOW_GRPC_ENABLED`, includes gRPC headers, and uses generated `file_transfer.pb.h` and `file_transfer.grpc.pb.h`. It integrates with the fdbrpc CMake gRPC/protobuf generation path and gRPC tests.

## Risks and Edge Cases
The API exposes raw filenames to remote callers, leaving access control/path restrictions to deployment context. Return values collapse all client errors to `std::nullopt`, making failure diagnosis coarse. Resume is not part of the public client API even though download requests support a first chunk index.

## Test Signals
The declarations are exercised by `FlowGrpcTests.cpp` file-transfer tests when gRPC support is enabled.

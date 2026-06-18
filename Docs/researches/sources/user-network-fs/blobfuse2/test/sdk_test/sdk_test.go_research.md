<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go -->
# sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go

Source path: `sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go`

## Purpose
Azure SDK comparison test that downloads and uploads blobs directly against Azure Blob Storage.

## Important APIs, Types, And Functions
Package functions: `TestMain`, `TestDownloadUpload`. Types: none declared. Imports: `context`, `fmt`, `io`, `os`, `path`, `time`, `errors`, `flag`, `testing`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/blob`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/blockblob`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/container`.

## Control Flow
Flags provide account, SAS, container, and blob prefix. The test builds a SAS container client, loops over six blob names, downloads each blob to `/mnt/ramdisk`, uploads it back using block blob upload, logs timings, and removes the local file.

## State And Persistence
Persists temporary files under `/mnt/ramdisk` and overwrites or updates the target blob names via SDK upload. Remote Azure state is part of the test surface.

## Dependencies And Integration Points
Integrates with Go's `testing` package, Azure Blob Storage SDK clients, SAS-authenticated container/blob URLs, `/mnt/ramdisk`, and remote Azure Blob state.

## Risks
Requires valid SAS credentials and network access. The test can mutate real blobs, and errors are often logged rather than failing immediately.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go -->

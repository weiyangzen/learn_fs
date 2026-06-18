<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/protos_test.go -->
# sources/storage-engines/badger/pb/protos_test.go

## Purpose
This file enforces that generated protobuf Go code is current with the checked-in `.proto` schema and generation script.

## Important APIs, Types, And Functions
`Exec` starts and waits for a command. `TestProtosRegenerate` runs `./gen.sh`, then `git diff --quiet -- badgerpb4.pb.go`.

## Control Flow
The test invokes the generator script from the test working directory, then asks Git whether the generated file changed. Any generator failure or resulting diff fails the test.

## State And Persistence Behavior
The test can rewrite `badgerpb4.pb.go` during execution and can install/update the protobuf generator through `gen.sh`. It relies on the repository being a Git checkout.

## Dependencies And Integration Points
It depends on `os/exec`, `testing`, `testify/require`, Bash, Go, `protoc`, and Git. It validates `badgerpb4.proto`, `gen.sh`, and `badgerpb4.pb.go` as a set.

## Risks And Edge Cases
This test is environment-sensitive: missing `protoc`, missing Git, no network/module cache, or running outside the expected directory can fail it. It has side effects on generated files and local tool installation.

## Test Signals
The signal is no error from regeneration and no diff in `badgerpb4.pb.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/protos_test.go -->

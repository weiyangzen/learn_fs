<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/gen.sh -->
# sources/storage-engines/badger/pb/gen.sh

## Purpose
This script regenerates Go protobuf bindings for `badgerpb4.proto`.

## Important APIs, Types, And Functions
It installs `google.golang.org/protobuf/cmd/protoc-gen-go@v1.31.0` and runs `protoc --go_out=. --go_opt=paths=source_relative badgerpb4.proto`.

## Control Flow
The script assumes it is run from its own directory so the proto file is in the current working directory. It first ensures the requested generator version is installed, then invokes `protoc` to write `badgerpb4.pb.go` beside the proto.

## State And Persistence Behavior
The script mutates the developer's Go tool installation/cache by installing `protoc-gen-go`, and rewrites generated source in the repository. It does not touch database files.

## Dependencies And Integration Points
It requires Bash, Go tooling, `protoc`, network/module availability if the generator is not cached, and the proto source file. It is called by `pb/protos_test.go`.

## Risks And Edge Cases
Running from another directory will fail because the proto path is relative. Different `protoc` binary versions can change generated output details, though the generator version is pinned. Environments without `protoc` or network access fail regeneration.

## Test Signals
`TestProtosRegenerate` runs this script and then checks that `badgerpb4.pb.go` has no git diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/gen.sh -->

# sources/storage-engines/badger/fb/gen.sh

## Purpose
`fb/gen.sh` regenerates Go FlatBuffers bindings from `flatbuffer.fbs`.

## Important APIs, Types, and Functions
This shell script sets `set -e`, checks for `flatc`, invokes `install_flatbuffers.sh` if missing, runs `flatc --go flatbuffer.fbs`, moves generated files from `fb/*` to the current directory, and removes the temporary `fb` directory.

## Control Flow and State
The script must be run from the `fb` directory so relative paths resolve. It exits on the first failing command. It assumes generated Go files land under a nested `fb` directory.

## Persistence Behavior
It rewrites generated source files such as `BlockOffset.go` and `TableIndex.go`; these files affect Badger's persisted table-index format through schema-compatible generated code.

## Dependencies and Integration Points
Depends on Bash, `flatc`, `flatbuffer.fbs`, `mv`, and `rmdir`. It may call `install_flatbuffers.sh`, which can use network/package managers.

## Risks and Edge Cases
The script is not hermetic: if `flatc` is absent, installation behavior varies by OS and may require sudo/network. Running from the wrong directory can move or remove unexpected paths. It does not pin the flatc version.

## Test Signals
No tests. Correctness is validated indirectly by generated code compiling and table/index tests passing.

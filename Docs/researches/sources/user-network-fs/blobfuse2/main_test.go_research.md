<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main_test.go -->
# sources/user-network-fs/blobfuse2/main_test.go

## Purpose
Coverage-oriented test for the binary entrypoint, excluded under the `unittest` build tag.

## Important APIs, Types, and Functions
`TestMain` filters `os.Args` to remove Go test flags, then invokes `main()` only if `os.Args[0]` contains `blobfuse2.test`; otherwise it records a test error.

## Control Flow and State
The test mutates global `os.Args`, which affects any later code in the same process. It uses the test binary name as a guard before invoking the real command entrypoint.

## Dependencies and Integration Points
Depends on standard `os`, `strings`, and `testing`. It integrates with the top-level `main` and transitively with the full command package, so it can trigger command initialization side effects.

## Risks and Edge Cases
Calling `main()` in a test can be brittle because command parsing may expect real CLI arguments, environment variables, or mount privileges. Mutating `os.Args` is process-global. The build tag keeps it out of unit-test mode, but coverage runs can still exercise broad startup behavior.

## Test Signals
Passing only indicates the test binary reached `main()` without failing this wrapper. It is not a focused assertion of CLI behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main_test.go -->

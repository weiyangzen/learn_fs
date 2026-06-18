<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go

## Purpose
Builds and runs the shared `posixtest` suite inside a QEMU guest mounted over virtiofs.

## Important APIs, Types, and Functions
`buildStaticPosixtest` and `TestPosixtest` are central.

## Control Flow
It compiles a static test binary, embeds it in the initrd, starts `ServeFS`, boots QEMU, mounts virtiofs, runs `posixtest.test` with DirectIO skipped, writes output and exit code into the host-backed mount, and parses failures.

## State and Persistence Behavior
State is temp initrd/socket, host loopback directory, QEMU process, and guest-generated output files.

## Dependencies and Integration Points
Integrates the POSIX suite with the full virtiofs/vhost-user/FUSE stack.

## Risks and Edge Cases
Same heavy environment risks as `fs_test.go`; parsing test output by regex may miss unusual failure formats; DirectIO is skipped.

## Test Signals
Signals include nonzero guest exit code, per-subtest failure lines, presence of `test_exit.txt`, and the `killme.txt` completion lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go -->

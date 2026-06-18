# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/3

## Purpose

This fixture is another Starnix parser input, representing a panic in `src/starnix/kernel/vfs/symlink_node.rs:28:5` with message `internal error: entered unreachable code: Symlink nodes cannot be opened.` It verifies that Starnix panic reports are classified by the application-level panic rather than by the later process teardown noise.

## Important Content And Control Flow

The log carries `TITLE:` and `REPORT:` regions, Starnix panic text, syz-executor EOF, Rust backtrace frames through `create_file_ops`, `FsNode::open`, `open_file_at`, `sys_openat`, and `sys_creat`, plus crashsvc exception processing and critical-process shutdown messages. The reporter must find the panic marker, preserve the relevant Rust path/function frames, and stop unrelated job death messages from becoming the report title.

## State, Dependencies, Integration, Risks, And Test Signals

The file is immutable test data for Starnix report extraction. It depends on the Starnix reporter regular expressions and symbolization conventions used by `pkg/report`. Risks include parser overmatching on `SYZFATAL`, missing the `REPORT:` copy of the panic, or being confused by BuildID/module lines. Passing tests show that syzkaller can normalize Starnix Rust panics from noisy Fuchsia kernel logs and keep symlink-open crashes distinct from other Starnix panics.

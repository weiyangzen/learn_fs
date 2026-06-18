# sources/user-network-fs/fusepy/examples/context.py

## Purpose
`context.py` is a read-only fusepy example filesystem demonstrating `fuse_get_context()`. It exposes three virtual files, `/uid`, `/gid`, and `/pid`, whose contents reflect the uid, gid, and pid of the process making the current FUSE request.

## Important APIs, Types, and Functions
- `Context(LoggingMixIn, Operations)`: implements a minimal filesystem.
- `getattr(path, fh=None)`: returns directory or read-only regular-file metadata, with current timestamps.
- `read(path, size, offset, fh)`: returns encoded uid/gid/pid values.
- `readdir(path, fh)`: lists `.`, `..`, `uid`, `gid`, `pid`.
- Disabled operations are set to `None` so fusepy does not register them.

## Control Flow
When mounted, FUSE dispatches getattr/read/readdir to `Context`. Each request calls `fuse_get_context()` to fetch kernel-supplied caller identity. The main block parses one `mount` argument, enables debug logging, and mounts foreground read-only with `allow_other=True`.

## State and Persistence
No persistent state is stored. File contents are computed per request from FUSE context and timestamps are current `time()`.

## Dependencies and Integration Points
It depends on fusepy’s `FUSE`, `Operations`, `LoggingMixIn`, `FuseOSError`, and `fuse_get_context`, plus errno/stat/time. It requires a working FUSE mount environment and may require configuration to allow `allow_other`.

## Risks and Edge Cases
`read()` ignores `size` and `offset`, returning full content for every request, which is acceptable for demonstration but not correct general filesystem behavior. `allow_other=True` can fail unless `/etc/fuse.conf` permits it. The example exposes request pid/uid/gid to readers by design.

## Test Signals
Mount the example, read the three files as different users/processes, and verify content matches request context. Also test stat output and partial reads to document demonstration limitations.

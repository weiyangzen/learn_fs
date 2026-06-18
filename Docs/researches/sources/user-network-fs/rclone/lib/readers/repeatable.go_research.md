# sources/user-network-fs/rclone/lib/readers/repeatable.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable.go -->
## sources/user-network-fs/rclone/lib/readers/repeatable.go

Purpose: implements a caching `io.ReadSeeker` that allows seeking within bytes already read from an underlying reader. It avoids rereading from the source while supporting limited replay.

Important APIs and control flow: `Read` serves from cache when `i < len(b)`; when positioned at cache end, it reads from `in`, appends any bytes read to cache, and advances `i`. `Seek` supports start/current/end relative to the cache length, rejects invalid whence, negative positions, and offsets beyond the cached bytes. Constructors create unsized, preallocated, limited, and caller-buffer-backed readers.

State, dependencies, and integration: `RepeatableReader` stores `in`, current index `i`, cached bytes `b`, and a mutex for concurrent method calls. It depends on `errors`, `io`, and `sync`. It integrates with upload/signing paths that need to replay already consumed request bodies without buffering the entire unknown stream in advance.

Risks and test signals: seeking cannot move beyond cached bytes, so callers must read before rewinding. Cache grows with all bytes read unless a limit reader is used. The mutex serializes operations but does not make the underlying reader itself independently safe for external concurrent use. Tests cover read, EOF, rewinds, partial reads, seek errors, and read-after-seek.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable.go -->

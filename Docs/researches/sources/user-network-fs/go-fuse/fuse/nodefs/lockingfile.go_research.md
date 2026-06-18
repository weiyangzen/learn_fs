## sources/user-network-fs/go-fuse/fuse/nodefs/lockingfile.go

Purpose: thread-safe wrapper for nodefs `File` implementations.

Important APIs/types/functions: `lockingFile` wraps a `File` with a mutex and delegates all operations while serializing access. Constructor helpers create the wrapper.

Control flow: each file method locks, calls the inner file, and unlocks. `InnerFile` exposes the wrapped file for unwrapping chains.

State and persistence: wrapper holds mutex and inner file reference; underlying file owns durable or in-memory data.

Dependencies and integration: useful for non-thread-safe file implementations returned to nodefs.

Risks and test signals: serialization avoids races but can deadlock if inner file calls back into code expecting the same lock. Behavioral coverage is indirect through concurrent file tests.

# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/openfile.rs

Purpose: Implements operations on an opened passthrough file handle.

Important APIs/types/functions: `PassthroughOpenFile::new` wraps `tokio::fs::File`. Helpers implement chmod, fchown, truncate, and futimens-style timestamp updates. `OpenFile` methods provide getattr, setattr, read, write, flush, and fsync.

Control flow: metadata operations act on the open file descriptor where possible. Reads and writes seek/read/write the host file through Tokio APIs. Flush and fsync delegate to file sync methods based on datasync.

State and persistence behavior: persistent state is the host file content and metadata. The wrapper owns only the open file handle.

Dependencies and integration points: returned by `PassthroughFile::into_open` and directory create/open. Uses `nix`, fd traits, and utility conversions.

Risks: descriptor cloning for fchown has overhead. Offset conversion and seek behavior need careful EOF/error handling. Host filesystem semantics may differ from object API expectations.

Test signals: cover read/write offsets, truncate through open handle, sync modes, setattr ownership/mode changes, and permission errors.

# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/file.rs

Purpose: Implements passthrough file node opening.

Important APIs/types/functions: `PassthroughFile::new` stores a path. The `File` impl consumes the async-drop guard, opens the host file with read/write options derived from `OpenInFlags`, and returns `PassthroughOpenFile`.

Control flow: `into_open` unwraps the guard without dropping, builds `tokio::fs::OpenOptions`, maps read/write/readwrite flags, opens the path, and wraps the file handle.

State and persistence behavior: no in-memory file data; persistence is the host file. Async drop is a no-op.

Dependencies and integration points: used by `PassthroughNode::as_file` and directory create/open paths.

Risks: opening does not pass through every kernel open flag such as append/truncate; it only models access mode. `unsafe_into_inner_dont_drop` is deliberate but must remain paired with no resource cleanup in the wrapper.

Test signals: cover open modes, permission errors, and read/write attempts through `PassthroughOpenFile`.

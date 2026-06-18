## sources/user-network-fs/go-fuse/fuse/context.go

Purpose: bridges FUSE caller metadata into Go `context.Context`.

Important APIs/types/functions: `Context` stores `*Caller` and implements `Deadline`, `Done`, `Err`, and `Value`. `FromContext` extracts caller data from a generic context. `NewContext` attaches caller metadata using a private key.

Control flow: raw request handling can wrap contexts with caller metadata; high-level code retrieves it without depending on concrete context type.

State and persistence: context values are per-request transient state.

Dependencies and integration: used by high-level fs/nodefs/pathfs callbacks to access UID/GID/PID or request ownership.

Risks and test signals: incorrect context propagation breaks permission-sensitive filesystems and idmapped/default-permission behavior.

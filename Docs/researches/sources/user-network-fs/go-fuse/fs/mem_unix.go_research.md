## sources/user-network-fs/go-fuse/fs/mem_unix.go

Purpose: non-Linux implementation of `keepSizeMode`, a platform hook used by in-memory file allocation/truncation behavior.

Important APIs/types/functions: `keepSizeMode(mode uint32) bool` always returns false under `!linux`.

Control flow: callers branch on the boolean to decide whether an allocation mode preserves file size. On non-Linux platforms, the path never treats the mode as keep-size.

State and persistence: stateless helper; no persistence or external state.

Dependencies and integration: selected by Go build tags for non-Linux `fs` builds, complementing the Linux-specific in-memory file implementation.

Risks and test signals: platform divergence is intentional. Any feature relying on Linux fallocate keep-size semantics must handle false here or remain Linux-only.

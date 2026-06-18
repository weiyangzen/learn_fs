<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go

Purpose: shared strict JSON decoder helper that rejects trailing tokens after a top-level value.

Important APIs, types, and functions: defines `TrailingDataError` and `mustEOF`.

Control flow: `mustEOF` asks the decoder for another token; `io.EOF` is success, a token becomes `TrailingDataError`, and other errors propagate.

State and persistence behavior: no persistent state.

Dependencies and integration points: used by both HTTP JSON client and server to enforce exact one-message bodies.

Risks and test signals: error wording mimics JSON syntax errors. Tests should cover trailing whitespace, trailing objects, and malformed data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go -->

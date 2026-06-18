## sources/user-network-fs/go-fuse/fuse/opcode.go

Purpose: raw FUSE opcode registry and dispatch functions for protocol requests.

Important APIs/types/functions: opcode constants, `doInit`, operation-specific `do*` handlers, `operationHandler`, `operationHandlers`, `operationName`, `getHandler`, and `checkFixedBufferSize`. Handlers parse request input, call `RawFileSystem`, fill output structs, and set status.

Control flow: package init builds handler table names, functions, input/output sizes, filename counts, and suppress-reply flags. Runtime request processing finds handlers by opcode and invokes the appropriate `do*` function.

State and persistence: global handler table and `maxInputSize`; server-specific state includes kernel settings, options, and notify retrieve tables.

Dependencies and integration: core dispatch layer used by `protocolServer` and every raw/high-level FS.

Risks and test signals: protocol layout, capability negotiation, xattr sizing, forget handling, and fixed buffer sizes are high risk. Many tests indirectly cover this; platform opcode tests cover extensions.

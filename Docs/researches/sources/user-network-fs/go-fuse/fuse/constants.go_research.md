## sources/user-network-fs/go-fuse/fuse/constants.go

Purpose: defines portable FUSE and syscall-adjacent constants used across the package.

Important APIs/types/functions: constants include open flags, file mode bits, status-related values, FUSE IDs, and defaults shared by mount and protocol code.

Control flow: no executable flow; compile-time values are imported by request handlers, mount code, and adapters.

State and persistence: none.

Dependencies and integration: platform-specific constants files fill in values that differ across Linux and FreeBSD.

Risks and test signals: incorrect constants break wire protocol interpretation or option negotiation. Failures surface broadly in mount, open, mode, and xattr tests.

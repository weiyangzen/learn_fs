## sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.h

Purpose: Shared declarations for the `nfsref` utility implementation files.

Important APIs/types/functions: Defines `enum nfsref_type` with unspecified, NFS basic, and NFS FedFS values, plus prototypes for add/remove/lookup handlers and help functions.

Control flow: No executable flow; it stabilizes the front-end-to-subcommand contract.

State and persistence: No state. Type values determine which persistence backend a subcommand attempts to use.

Dependencies and integration: Included by all `nfsref` C files and built as a no-install local header.

Risks and test signals: FedFS type is declared but not implemented in the researched command paths, so tests should verify graceful rejection rather than accidental partial behavior.

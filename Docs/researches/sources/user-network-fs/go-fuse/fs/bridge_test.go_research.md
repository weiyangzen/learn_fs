# sources/user-network-fs/go-fuse/fs/bridge_test.go

Purpose: targeted tests for raw bridge behavior around readdirplus virtual entries, inode type changes, orphan paths, inode number 1, negative lookup caching, and nil options.

Important tests: `TestBridgeReaddirPlusVirtualEntries` inspects raw buffer layout to ensure `.`/`..` have `NodeId` zero; `TestTypeChange` reuses inode number with changing file type; `TestDeletedInodePath` verifies orphan paths get `.go-fuse.../deleted`; `TestIno1` allows inode number 1; `TestNegativeLookupCache` checks lookup counts with/without negative TTL; `TestNewNodeFSNilOpts` ensures defaults.

State/dependencies: uses real FUSE mounts plus in-memory test nodes.

Risks/test signals: covers subtle kernel cache and stable-attr behavior. It is sensitive to low-level buffer layout and FUSE mount support, but gives strong regression signals for bridge invariants.

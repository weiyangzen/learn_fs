<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.NodeGetattrer)((*Node)(nil))`, `var _ = (fs.NodeLookuper)((*Node)(nil))`, `var _ = (fs.NodeReaddirer)((*Node)(nil))`, `var _ = (fs.NodeReadlinker)((*Node)(nil))`, `var _ = (fs.NodeOpener)((*Node)(nil))`, `var _ = (fs.NodeStatfser)((*Node)(nil))`, `var _ = (fs.NodeGetxattrer)((*Node)(nil))`, `var _ = (fs.NodeListxattrer)((*Node)(nil))`, `var _ = (fs.NodeOpendirer)((*Node)(nil))`, `var _ = (fs.NodeMknoder)((*Node)(nil))`, `var _ = (fs.NodeCreater)((*Node)(nil))`, `var _ = (fs.NodeMkdirer)((*Node)(nil))` (9 more declarations in file).
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 1070 bytes across 35 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go -->

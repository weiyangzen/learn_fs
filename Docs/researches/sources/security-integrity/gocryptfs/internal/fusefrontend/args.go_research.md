<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/args.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/args.go

- Purpose: Defines the forward/reverse frontend configuration surface passed from main into FUSE operations.
- Important APIs/types/functions: `type Args struct`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 2293 bytes across 57 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fuse. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/args.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/args.go -->

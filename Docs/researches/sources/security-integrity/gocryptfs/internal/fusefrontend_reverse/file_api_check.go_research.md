<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the file_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.FileReader)((*File)(nil))`, `var _ = (fs.FileReleaser)((*File)(nil))`, `var _ = (fs.FileLseeker)((*File)(nil))`, `var _ = (fs.FileGetattrer)((*File)(nil))`, `var _ = (fs.FileGetlker)((*File)(nil))`, `var _ = (fs.FileSetlker)((*File)(nil))`, `var _ = (fs.FileSetlkwer)((*File)(nil))`, `var _ = (fs.FileSetattrer)((*File)(nil))`, `var _ = (fs.FileWriter)((*File)(nil))`, `var _ = (fs.FileFsyncer)((*File)(nil))`, `var _ = (fs.FileFlusher)((*File)(nil))`, `var _ = (fs.FileAllocater)((*File)(nil))`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 688 bytes across 26 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go -->

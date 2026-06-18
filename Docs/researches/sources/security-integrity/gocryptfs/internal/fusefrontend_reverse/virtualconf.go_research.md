<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go

- Purpose: Provides read-only virtual access to a generated reverse-mode config file.
- Important APIs/types/functions: `type VirtualConfNode struct`, `type VirtualConfFile struct`, `var _ = (fs.NodeOpener)((*VirtualConfNode)(nil))`, `var _ = (fs.NodeGetattrer)((*VirtualConfNode)(nil))`, `var _ = (fs.FileReader)((*VirtualConfFile)(nil))`, `var _ = (fs.FileReleaser)((*VirtualConfFile)(nil))`, `func (n *VirtualConfNode) rootNode() *RootNode`, `func (n *VirtualConfNode) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (n *VirtualConfNode) Getattr(ctx context.Context, fh fs.FileHandle, out *fuse.AttrOut) syscall.Errno`, `func (f *VirtualConfFile) Read(ctx context.Context, buf []byte, off int64) (res fuse.ReadResult, errno syscall.Errno)`, `func (f *VirtualConfFile) Release(ctx context.Context) syscall.Errno`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 1709 bytes across 76 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, sync, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go -->

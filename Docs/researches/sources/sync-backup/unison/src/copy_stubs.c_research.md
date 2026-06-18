# sources/sync-backup/unison/src/copy_stubs.c

Purpose: platform-specific OCaml C stubs for efficient file clone/copy operations.

Important APIs: `unison_clone_path(src,dst)` for macOS `clonefile`; `unison_clone_file(in_fd,out_fd)` for Linux `FICLONE`; `unison_copy_file(in_fd,out_fd,in_offs,len)` for Linux `copy_file_range`/`sendfile`, FreeBSD `copy_file_range`, Solaris `sendfile`, Windows ReFS `FSCTL_DUPLICATE_EXTENTS_TO_FILE`, or `ENOSYS` fallback.

Control flow: clone APIs must never raise and return boolean success. Copy APIs release the OCaml runtime around blocking syscalls, return copied byte count, or raise Unix errors. Linux tries `copy_file_range` first, then `sendfile` on unsupported/cross-device-like failures. Windows validates block-clone support on both handles, reads integrity/cluster size, checks cluster alignment, toggles sparse status when needed, extends destination length, performs extent duplication, and advances the output file pointer manually.

State/persistence: changes destination file contents, length, sparseness, and file offset. Source offset is protected by explicit offsets where platform APIs allow.

Dependencies/integration: OCaml runtime/unixsupport compatibility shims, OS clone/copy syscalls, Windows HANDLE APIs, MinGW compatibility typedefs, and filesystem support such as APFS/ReFS/Btrfs/XFS.

Risks: platform behavior is subtle: partial `sendfile`, cluster-alignment requirements on Windows, unsupported filesystem paths, sparse toggling, and offset semantics differ. Windows code assumes source and destination cluster size compatibility on the same ReFS volume.

Test signals: copy tests should cover unsupported fallback, partial return handling, offset preservation, output offset advancement, sparse files, cross-device behavior, large files, and Windows aligned/unaligned extents.

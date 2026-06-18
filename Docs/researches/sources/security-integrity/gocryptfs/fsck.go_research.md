# sources/security-integrity/gocryptfs/fsck.go

Purpose: This file implements gocryptfs filesystem checking over encrypted storage, detecting corrupt filenames, unreadable files, xattr errors, symlink issues, and mitigated corruption warnings.

Important APIs and functions: `fsckObj` carries counters, root paths, crypto/name transformers, and options. Methods include `markCorrupt`, `markSkipped`, `abs`, `dir`, `file`, `symlink`, `xattrs`, and watcher helpers for mitigated corruptions during open/read/listxattr. `fsck(args)` is the main entrypoint.

Control flow and state: `fsck` loads config, initializes crypto, walks directories recursively, optionally respects one-filesystem boundaries, decrypts names, reads file blocks through gocryptfs logic, checks symlink targets, and tallies corrupt/skipped entries. It persists no repairs, only diagnostics and exit code.

Dependencies and integration points: Integrates configfile, content encryption, name encryption, syscall compatibility, FUSE-like read paths, xattr handling, and CLI flags.

Risks and test signals: Corruption checks can trigger reads over large trees and must avoid crossing filesystems when requested. Signals include expected exit codes, corrupt/skipped counters, and fixture tests with damaged names/data/xattrs.

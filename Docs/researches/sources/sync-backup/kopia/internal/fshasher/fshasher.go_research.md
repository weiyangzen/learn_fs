# sources/sync-backup/kopia/internal/fshasher/fshasher.go

Purpose: computes a deterministic hash of a Kopia `fs.Entry` tree for tests by serializing metadata and file contents as a tar stream and hashing it with BLAKE2s-256.

Important APIs/types/functions: `Hash`, `write`, `header`, `writeDirectory`, and `writeFile`. It consumes `fs.Entry`, `fs.Directory`, `fs.File`, `fs.Symlink`, `fs.GetAllEntries`, `tar.Writer`, `blake2s.New256`, and `iocopy.JustCopy`.

Control flow: `Hash` creates the hasher and tar writer, then recursively writes the root entry. `write` emits a tar header, then dispatches by entry type: directories are listed, sorted by name, and recursively serialized; files are opened and copied; symlinks rely on link target in the header.

State/persistence behavior: no state is persisted. Directory modification times are zeroed, all times are truncated to second precision and UTC, and directory entries are sorted to reduce filesystem-dependent noise.

Dependencies/integration: integrates with Kopia's virtual filesystem interfaces and logging. Used as a test fingerprint when comparing restored or mock filesystem trees.

Risks/test signals: tar header semantics mean permissions, size, symlink targets, and truncated times affect hashes. File content reads are streamed, so read/open errors propagate. The second-resolution timestamp normalization may intentionally hide subsecond differences.

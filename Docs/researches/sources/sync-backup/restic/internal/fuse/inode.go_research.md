## sources/sync-backup/restic/internal/fuse/inode.go

Purpose: deterministic inode generation for FUSE pseudo directories and snapshot contents on Darwin, FreeBSD, and Linux builds.

Important APIs: `inodeFromName(parent, name)` hashes a cleaned filename with its parent inode using xxhash and a fixed prime. `inodeFromNode(parent, node)` uses `(DeviceID, Inode)` for non-directory hard links so all hard-link instances share one inode; otherwise it hashes the cleaned node name with the parent inode. Both remap inode values `0` and `1` away from invalid/root-reserved values.

Control flow and state: this file is pure computation and has no persistence. It relies on `cleanupNodeName` from the FUSE directory code before hashing names, so character normalization in that helper affects inode stability.

Dependencies and integration points: imports `encoding/binary`, `github.com/cespare/xxhash/v2`, and `data.Node`. Results feed `fuse.Attr.Inode` in file, directory, symlink, other-node, and snapshot-directory paths.

Risks and test signals: collision risk is bounded by 64-bit hashing but not impossible; inode stability depends on preserving the hash algorithm and cleanup behavior. `TestInodeFromNode` covers hard-link same-inode behavior and a regression where nested repeated names could collide with ancestors. `BenchmarkInode` tracks allocation/performance expectations.

# sources/user-network-fs/gcsfuse/internal/fs/inode/inode.go

## Purpose

`inode.go` defines the core inode interfaces and generation comparison primitive used by the gcsfuse filesystem layer. It is a contract file: concrete directory, file, symlink, and explicit directory inodes conform to these interfaces so FUSE operation code can lock, inspect, update, destroy, and unlink inode objects uniformly.

## Important APIs, Types, And Functions

`Inode` embeds `sync.Locker` and defines identity (`ID`, `Name`), lookup-count management (`IncrementLookupCount`, `DecrementLookupCount`), current FUSE attributes, size update, destruction, and unlink marking. The comments establish the locking contract: most methods require the inode lock unless documented otherwise, while `ID` and `Name` do not.

`BucketOwnedInode` extends `Inode` with `Bucket() *gcsx.SyncerBucket`, allowing callers to find the owning bucket for file/dir operations. `GenerationBackedInode` extends `Inode` with `SourceGeneration() Generation`, used where delete, rename, sync, or clobber logic needs the exact GCS generation/metageneration backing an inode.

`Generation` stores `Object`, `Metadata`, and `Size`. `Generation.Compare` orders latest GCS state against current inode state: object generation first, metadata generation second, then a special size-growth case. It returns `-1`, `0`, `1`, or `2`; `2` means object/metageneration match but latest size is greater, a zonal/rapid append scenario.

## Control Flow And State Behavior

The file contains no persistence logic itself, but its contracts drive state transitions in implementations. `DecrementLookupCount` returning true tells inode managers to call `Destroy` after lookup references reach zero. `UpdateSize` allows directory/file code to refresh cached inode size after remote append detection. `Unlink` marks inodes deleted locally even before or independent of remote storage mutation.

`Generation.Compare` intentionally ignores the case where latest size is smaller than current size if object/metageneration match, returning `0`; comments say small staleness in GCS object size is expected. That choice affects clobber handling in `FileInode.Attributes` and `FileInode.Sync`.

## Dependencies And Integration Points

Dependencies are small: `sync`, `gcsx`, FUSE inode IDs, and context. The interfaces are consumed across the inode package and higher-level filesystem operation managers. `Generation.Compare` is used by file clobber detection and generation-backed explicit directory/file handling.

## Risks And Test Signals

Risks include interface contract drift, especially lock requirements and destruction semantics, and misinterpreting `Compare` return code `2` as ordinary greater-than. The size-shrink ignored case is deliberate but can mask certain stale-size observations. `inode_test.go` covers all comparison branches, including object, metadata, equal, larger-size, and smaller-size cases.

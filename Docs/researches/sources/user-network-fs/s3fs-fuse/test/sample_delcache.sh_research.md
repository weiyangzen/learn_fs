# sources/user-network-fs/s3fs-fuse/test/sample_delcache.sh

## Purpose
Unsupported sample script for pruning s3fs local cache files by access time until a byte-size limit is met.

## Important APIs, Types, And Control Flow
Parses bucket, cache path, byte limit, and optional `-silent`. Computes file and stat cache directories, exits if under limit, then finds stat files with atime, sorts oldest first, maps stat-file paths to cache-file paths, validates unchanged atime, removes both files, and stops once current cache size is below limit.

## State And Persistence
Deletes files under `${cache}/${bucket}` and `${cache}/.${bucket}.stat`. It can permanently remove local cached object/stat data, though remote S3 data should remain.

## Dependencies And Integration Points
Uses POSIX shell plus GNU `du -sb`, `stat -c`, find, sort, cut, sed, and rm. It is a sample helper for installations using `use_cache`, not part of `make check`.

## Risks And Test Signals
Not safe for all platforms because GNU-specific `du`/`stat` options are used. It can race active s3fs cache users and does not lock. Path mapping via sed can fail for unusual bucket/cache names. Test on disposable cache directories before operational use.

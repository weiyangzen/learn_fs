# sources/object-store/minio-mc/cmd/client-fs_test.go

## Purpose

This test file validates the local filesystem `Client` implementation against common mc client operations. It focuses on basic file and directory semantics rather than every S3-compatible method stub.

## Important Tests And Control Flow

`TestList` creates temporary files through `fsClient.Put`, verifies nonrecursive and recursive listings, counts regular files/directories, and checks `.DS_Store` filtering differences on Darwin versus other platforms. `TestPutBucket` and `TestStatBucket` exercise `MakeBucket` and `Stat` for directory paths. `TestBucketACLFails` confirms chmod-style access works for directories on non-Windows platforms. `TestPut`, `TestGet`, `TestGetRange`, and `TestStatObject` cover file write, readback, reader-at access, and size metadata. `TestCopy` creates a source file and copies it to a target filesystem client.

## Dependencies, Risks, And Signals

The tests use temporary directories, `gopkg.in/check.v1`, `bytes`, `io`, `filepath`, and runtime OS checks. They signal that basic temp-file commit, list ordering/filtering, stat metadata, and local copy are expected to work. Gaps remain around remove recursion, watch events, preserve/xattr behavior, partial put through `PutPart`, path-length errors, symlink loops, and unsupported S3 API methods.

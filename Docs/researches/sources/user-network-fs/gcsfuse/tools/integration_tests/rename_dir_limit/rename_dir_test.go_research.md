# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_test.go

## Purpose

This file validates `--rename-dir-limit=3` behavior and destination-directory rename semantics. It checks success at or below the object limit, failure above the limit for flat buckets, and behavior when the destination directory already exists.

## Important APIs, Types, and Functions

Tests create directory trees using `operations.CreateDirectoryWithNFiles` and rename using `os.Rename` or Python `os.rename` via `exec.Command`. Cases cover three files, two files, four files, two files plus empty directory, two files plus non-empty directory, existing empty destination, and existing non-empty destination. `setup.ResolveIsHierarchicalBucket` skips flat-limit failure expectations on hierarchical buckets.

## Control Flow

Success cases create a source directory whose object count is at or below the limit, remove any stale destination, call `os.Rename`, and expect no error. Failure cases create more than the limit and expect `os.Rename` to fail unless the bucket is hierarchical. Existing-destination cases use Python because Go's `os.Rename` wrapper does not support the exact directory overwrite behavior being tested; the non-empty destination case expects `ENOTEMPTY`.

## State and Persistence Behavior

The tests create and rename mounted directories backed by GCS objects. Successful renames remove old paths and populate new paths. Failure cases should leave source data intact, though not all failure tests explicitly revalidate source preservation.

## Dependencies and Integration Points

It depends on setup constants/globals from the harness, operations helpers, standard `os/exec/syscall`, and `testify/assert`. It is coupled to flat bucket rename emulation and HNS native rename semantics.

## Risks and Edge Cases

The comment for the four-file test says "two, greater than limit" but the code creates four files. Object-count semantics around empty directories differ between flat and hierarchical buckets. Python command construction embeds paths directly into source strings; unusual quotes in paths would be unsafe, though generated test paths are controlled. Existing empty-destination behavior is platform/FUSE specific.

## Test Signals

Passing confirms limit boundary behavior, over-limit rejection for flat buckets, source-to-existing-empty replacement behavior, and `ENOTEMPTY` for existing non-empty destinations. Failures indicate rename limit counting, recursive rename, or destination conflict handling regressions.

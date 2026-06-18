# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readlink.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for reading symlink targets. It measures symlinks in the root directory, a nested directory, a deeply nested directory, and a symlink with a long target string that spans multiple backing nodes.

## Important APIs, types, and functions
- Registers `from_rootdir`, `from_nesteddir`, `from_deeplynesteddir`, and `long_target`.
- Setup uses `FilesystemDriver::create_symlink`, plus `mkdir` or `mkdir_recursive` for parent directories.
- The measured operation is `FilesystemDriver::readlink`.
- Uses `AtimeUpdateBehavior` to decide whether symlink atime should be persisted: `Strictatime` and `NodiratimeStrictatime` update, while `Noatime`, `Relatime`, and `NodiratimeRelatime` do not.
- The long-target case constructs a target by repeating `"/very/long"` based on `NUM_BYTES_FOR_THREE_LEVEL_TREE`.

## Control flow
Each case creates a symlink and returns its node handle from setup. The test body calls `readlink(symlink).await.unwrap()`. Expected counts branch on fixture type, path depth, target length, and atime policy. The long-target case remains rooted at `/` but expects many high-level and low-level loads because the symlink payload spans a larger blob tree.

## State and persistence behavior
Readlink returns symlink target data without changing the link content. Under strict atime modes it writes timestamp metadata, adding a single blob write/resize and low-level store. The long-target setup persists a large symlink target so the measured read has larger tree traversal cost but the same atime update shape.

## Dependencies and integration points
The file depends on the filesystem driver's symlink representation, CryFS path parsing, atime configuration, and fixture-specific caching behavior. It shares the same tracking-store counters as the rest of the operation suite. The expected counts reveal that fuser without inode cache performs extra loads proportional to path depth.

## Risks and observations
The count formulas are annotated with TODOs asking whether they are expected, and the operation registry questions whether atime behavior is consistently represented across operations. The distinction between `Relatime` and `Strictatime` here differs from some read-file cases, so future atime fixes may require coordinated changes.

## Test signals
The suite verifies path-depth scaling for symlink lookup, strict-atime write behavior for symlink reads, and multi-block payload traversal for long symlink targets. It also provides benchmark coverage for readlink latency across fixture drivers and atime policies.

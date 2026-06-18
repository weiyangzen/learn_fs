# sources/user-network-fs/mergerfs/src/fs_sendfile.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_sendfile.cpp` selects the platform sendfile implementation at compile time. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

Includes the Linux implementation on Linux and an unsupported implementation elsewhere.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_sendfile_linux.icpp", "fs_sendfile_unsupported.icpp". Provides backend transfer support; behavior depends on the included `.icpp`.

## Risks and Edge Cases

Provides backend transfer support; behavior depends on the included `.icpp`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.

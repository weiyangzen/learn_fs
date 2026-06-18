# sources/user-network-fs/nfs-utils/support/include/misc.h

## Purpose
Collects small shared support declarations for random keys, state path helpers, mountpoint checks, and RPC procfs buffer sizing.

## Important APIs, Types, and Functions
Declares `randomkey()`, `weakrandomkey()`, `generic_make_pathname()`, `generic_setup_basedir()`, `check_is_mountpoint()`, `is_mountpoint()`, and `RPC_CHAN_BUF_SIZE`.

## Control Flow
Implementations allocate state paths, validate base directories, generate keys, and determine mountpoints by stat comparisons.

## State and Persistence Behavior
No state is stored here. Implementations may inspect filesystem state and return heap path strings.

## Dependencies and Integration Points
Used by export state setup, mountpoint checks, and procfs cache readers.

## Risks and Edge Cases
Weak random keys are explicitly not strong. Mountpoint checks rely on stat behavior and symlink/lstat choice.

## Test Signals
Test path length limits, base directory validation, mountpoint detection, and randomkey length/error behavior.

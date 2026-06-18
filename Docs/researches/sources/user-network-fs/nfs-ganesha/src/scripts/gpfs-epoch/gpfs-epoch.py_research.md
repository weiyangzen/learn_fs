# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/gpfs-epoch.py

## Purpose

`gpfs-epoch.py` generates a cluster-unique Ganesha epoch for GPFS environments by combining the GPFS node ID with a local generation number.

## Important APIs, Types, and Functions

`main`, `get_genid`, `put_genid`, `get_mount`, and `get_nodeid` implement the epoch calculation. `GracePeriodArg` and `KxArgs` are ctypes structures used for the GPFS ioctl. Constants include `epoch_file`, `GPFS_DEVNAMEX`, `kGanesha`, and `OPENHANDLE_GET_NODEID`.

## Control Flow

`main` increments and stores the generation ID, discovers the GPFS node ID via `get_nodeid`, combines the two fields into a 32-bit epoch, and prints it. `get_mount` parses `mount` command output for a GPFS mount point. `get_nodeid` opens `/dev/ss0` and the GPFS mount directory, builds ioctl argument structs, and calls `fcntl.ioctl`.

## State and Persistence Behavior

The persistent state is `/var/lib/nfs/ganesha/gpfs-epoch`, updated on each run. The script also opens GPFS device and mount directory file descriptors.

## Dependencies and Integration Points

It depends on GPFS device `/dev/ss0`, a mounted GPFS filesystem, platform-specific `mount`, `fcntl.ioctl`, ctypes structure layout matching GPFS headers, and syslog for exception reporting. It is installed by the GPFS epoch CMake package.

## Risks and Edge Cases

There is no locking or atomic write for the generation file. `get_mount` may return `None`, causing `os.open(None, ...)`. File descriptors are not explicitly closed. Generation wraps at 16 bits. The ioctl structure is hand-coded and sensitive to platform ABI.

## Test Signals

Unit tests can mock mount output, generation file access, and ioctl return values. Integration tests require GPFS and should verify epoch uniqueness across nodes/restarts and failure logging when GPFS is unavailable.

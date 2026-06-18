# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fd/fdops.c

## Purpose
Implements the `/dev/fd` pseudo-filesystem. It exposes per-process file descriptor numbers as character-device vnodes under a mounted directory.

## Main Responsibilities
- Registers and initializes the `fd` filesystem module.
- Provides VFS mount/unmount/root/statvfs operations.
- Provides vnode operations for directory reads/lookups and synthetic descriptor vnodes.
- Generates entries based on the current process file table and `RLIMIT_NOFILE`.

## Core Constants and State
- `FDROOTINO`: inode number for root directory.
- `fdtoi(n)`: maps fd number to synthetic inode number.
- `FDSDSIZE`, `FDNSIZE`: directory-entry sizing/name limits.
- `fdfstype`, `fdfsmaj`, `fdfsmin`, `fdrmaj`: filesystem and device numbering.
- `fd_minor_lock`: serializes pseudo-device minor allocation.

## Vnode Operations
`fd_vnodeops_template` includes:
- `fdopen()`: marks non-directory vnodes `VDUP`, allowing open to duplicate the referenced fd semantics.
- `fdclose()`: no-op.
- `fdread()`: legacy directory-format read for the root directory.
- `fdgetattr()`: synthetic stat data for root or fd entries.
- `fdaccess()`: permits all access.
- `fdlookup()`: maps `"."`, `".."`, or numeric names to vnodes.
- `fdcreate()`: treats create as lookup for numeric fd entries.
- `fdreaddir()`: emits `dirent64` records.
- `fdinactive()`: releases and frees transient vnodes.

Unsupported operations include frlock, poll, dispose.

## Directory Enumeration
Both `fdread()` and `fdreaddir()` compute entry count from:
- `P_FINFO(curproc)->fi_nfiles`
- enforced `RLIMIT_NOFILE`

Entries include `"."`, `".."`, then numeric names from `0` to allowed max minus one. These are not filtered for currently open descriptors; `/dev/fd/N` lookup creates a vnode for numeric `N`, and later open behavior resolves duplication elsewhere in the kernel path.

`fdreaddir()` advances offsets in fixed `FDSDSIZE` increments even though returned `dirent64` record lengths vary.

## Vnode Creation
`fdget()`:
- Parses component name as decimal digits only.
- Allocates a transient `VCHR` vnode.
- Uses fd vnode ops, `VNOMAP`, and `makedevice(fdrmaj, n)`.
- Does not validate that fd `n` is open at lookup time.

## VFS Operations
`fdmount()`:
- Requires mount privilege and directory mount point.
- Enforces non-overlay busy checks.
- Sets resource name to `"fd"`.
- Allocates the root vnode, assigns unique pseudo-device minor, sets fsid and block size.

`fdunmount()`:
- Requires unmount privilege.
- Rejects forced unmount.
- Refuses if root vnode has extra refs, otherwise releases it.

`fdroot()`:
- Returns a held root vnode.

`fdstatvfs()`:
- Reports zero block capacity, synthetic file count, name max, basetype, flags, fsid, and `/dev/fd` strings.

`fdinit()`:
- Installs VFS ops and vnode ops.
- Gets unique device majors for filesystem and descriptor nodes.
- Initializes minor lock.

## Module Registration
Defines mount options defaulting to read-write and ignore support, then registers as filesystem `"fd"` with `VSW_HASPROTO | VSW_ZMOUNT`.

## Integration Points
- VFS operation registration via `vfs_setfsops()`.
- Vnode operation creation via `vn_make_ops()`.
- Resource controls via `rctl_enforced_value()`.
- File table sizing via `P_FINFO(curproc)`.
- Device number helpers `getudev()`, `makedevice()`, `vfs_make_fsid()`.

## Risks and Subtle Areas
- Directory listings are based on allowed descriptor range, not open descriptors, which can surprise consumers but matches `/dev/fd` semantics.
- `fdget()` accepts arbitrary numeric values without range or open checks.
- Root vnode lifetime is simple but unmount depends on `v_count` being exactly manageable.
- `fdread()` uses old fixed-size directory records; `fdreaddir()` uses modern `dirent64`.

## Testing/Validation Signals
- Mount/unmount `/dev/fd` with/without overlay and busy root refs.
- `readdir()` under different `RLIMIT_NOFILE` values.
- Lookup numeric and nonnumeric names.
- Open non-directory fd vnode and verify duplication behavior through broader `/dev/fd` stack.

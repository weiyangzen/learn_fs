# File System Source Repository List

Generated from a 10-agent debate workflow on 2026-06-15.

## Boundary

`learn_fs` is a source-only corpus for local filesystems, OS VFS layers,
network filesystems, distributed/parallel filesystems, object-store
adjacent storage, container/virtualized storage, filesystem tools, tests,
security/integrity/sync systems, and selected storage engines that
directly teach filesystem mechanisms.

It does not collect papers, blogs, docs sites, prebuilt packages, binary
release payloads, VM images, container layers, benchmark datasets, closed
product internals, leaked source, or proprietary-only systems.

The manifest currently contains:

- `required`: 59 repositories
- `important`: 119 repositories
- `adjacent`: 36 repositories
- default-counted for source LOC: 144 repositories

## Authoritative Local Files

- `manifests/sources.tsv` - canonical cloneable source list
- `manifests/focus_paths.tsv` - must-check reading paths
- `scripts/clone_sources.sh` - shallow partial clone driver
- `scripts/lock_remotes.sh` - remote HEAD/ref lock report
- `scripts/verify_sources.sh` - manifest and checkout verifier
- `scripts/source_inventory.py` - source-like LOC counter

## Complete Source Families

The complete public-source boundary is represented by these families:

- OS/VFS: Linux, FreeBSD, OpenBSD, NetBSD, DragonFly BSD, illumos, Plan 9/9front, ReactOS, public Windows FS frameworks/samples.
- Local FS and tools: ext, XFS, Btrfs, F2FS, EROFS, ZFS, bcachefs, NILFS, bcache, FAT/exFAT, NTFS, UDF, JFS, SquashFS, APFS public readers, device-mapper/LVM/VDO/Stratis.
- User/network FS: FUSE, SSHFS, NFS, NFS-Ganesha, SMB/Samba/CIFS/KSMBD, WebDAV, object-store mount layers.
- Distributed FS: CephFS, GlusterFS, Lustre, BeeGFS, MooseFS/LizardFS, OrangeFS, HDFS, Alluxio, JuiceFS, SeaweedFS, OpenAFS, Coda, XRootD/EOS, Tahoe-LAFS, Kubo/IPFS as content-addressed contrast.
- Object-store adjacent: MinIO, Swift, Ozone, DAOS, Garage, RustFS, relevant CSI/control-plane source.
- Cloud/virtualized storage: fuse-overlayfs, containers/storage, containerd snapshotters, stargz, Nydus, SOCI, composefs, OSTree, QEMU block, virtiofsd, SPDK, NBD.
- Testing/tools: xfstests, blktests, fio, LTP, pjdfstest, stress-ng/iozone and filesystem mkfs/fsck/repair tools.
- Security/integrity/sync: fscrypt, fsverity, encrypted FUSE filesystems, IMA/EVM, rsync, Syncthing, Restic, Borg, Kopia, git-annex, casync.
- Storage engines: RocksDB, LevelDB, Badger, Pebble, WiredTiger, SQLite, LMDB, FoundationDB, TiKV, raft-engine as adjacent source for WAL, LSM, page cache, checkpoints, object/tiered storage, and replicated logs.

## Explicit Exclusions

- GPFS/Spectrum Scale, WekaFS, PanFS, Quobyte and similar systems without complete public source.
- Proprietary Windows NTFS/ReFS internals, WRK/leaked code, closed backup agents, closed cloud-drive clients.
- Firmware blobs, kernel prebuilts, package payloads, ISO/VM/container images, object-store datasets, benchmark outputs.
- Generic cloud SDKs, Kubernetes backup operators, UI wrappers, scheduler wrappers, and distro packaging recipes unless a patch changes source behavior relevant to filesystems.
- Papers/blogs/PDFs as repository content. External documentation can be cited in notes, but the study corpus is source.

## Study Order

1. Linux VFS, page cache, block layer, and core local filesystems.
2. Userspace mkfs/fsck/repair tools for ext/XFS/Btrfs/F2FS/EROFS/ZFS/bcachefs.
3. xfstests, LTP, fio, blktests, pjdfstest for behavior and failure cases.
4. FUSE, NFS, SMB/Samba, 9P, WebDAV and kernel/user protocol boundaries.
5. CephFS, GlusterFS, Lustre, BeeGFS, HDFS, JuiceFS, SeaweedFS, Alluxio.
6. BSD/illumos/Plan 9/ReactOS/Windows public source for cross-OS VFS comparison.
7. Container, image, object-store, security/integrity/sync, and storage-engine adjacent code.

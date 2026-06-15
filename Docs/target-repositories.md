# Target Source Repositories

Generated from `manifests/sources.tsv`.

This is the source-only target map for `learn_fs`. It is intentionally
broader than a single reading pass: `required` is the default clone
tier, `important` is part of the complete research boundary, and
`adjacent` covers source that is valuable for design comparison but can
be deferred when local disk or the 200M-line budget is tight.

## Tier Rules

- `required` - default source set for filesystem and distributed
  filesystem study.
- `important` - strong source additions needed for completeness or
  cross-platform comparison.
- `adjacent` - source that teaches nearby storage mechanisms, history,
  or implementation tradeoffs, but should not displace core FS source.

## Counting Rules

The line-count gate is 20,000,000 to 200,000,000 code-like lines for
checked-out source. Count source-like files from git-tracked trees;
exclude VCS metadata, build outputs, release archives, binary images,
firmware, VM/container images, package caches, generated artifacts, and
vendored dependency dumps unless a dependency is explicitly listed as a
source target here.

Two metrics should be reported:

- `focus-paths`: default. Count filesystem-relevant source paths listed
  in `manifests/focus_paths.tsv`, after generated/vendor/build/doc
  exclusions.
- `full-repo`: secondary audit. Count source-like files across each
  selected checkout after the same exclusions.

Use `focus-paths` as the primary gate so large monorepos such as Linux,
FreeBSD, QEMU, Hadoop, DAOS, Ceph, and containerd do not hide the
filesystem signal behind unrelated source.

## Repositories By Category

### block-storage

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `bcache-tools` | `sources/block-storage/bcache-tools` | https://git.kernel.org/pub/scm/linux/kernel/git/colyli/bcache-tools.git | yes | bcache userspace formatting registration and inspection. |
| required | `cryptsetup` | `sources/block-storage/cryptsetup` | https://gitlab.com/cryptsetup/cryptsetup.git | yes | LUKS dm-crypt verity integrity userspace. |
| required | `lvm2` | `sources/block-storage/lvm2` | https://gitlab.com/lvmteam/lvm2.git | yes | LVM libdevmapper dmsetup thin/cache metadata integration. |
| required | `thin-provisioning-tools` | `sources/block-storage/thin-provisioning-tools` | https://github.com/device-mapper-utils/thin-provisioning-tools.git | yes | dm-thin dm-cache dm-era metadata tools. |
| important | `kvdo` | `sources/block-storage/kvdo` | https://github.com/dm-vdo/kvdo.git | no | Historical/out-of-tree VDO kernel source. |
| important | `linux-dm` | `sources/block-storage/linux-dm` | https://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm.git | no | device-mapper maintainer kernel tree for dm targets. |
| important | `mdadm` | `sources/block-storage/mdadm` | https://git.kernel.org/pub/scm/utils/mdadm/mdadm.git | yes | Linux software RAID management source. |
| important | `parted` | `sources/block-storage/parted` | https://git.savannah.gnu.org/git/parted.git | yes | GPT MBR partitioning and disk layout tools. |
| important | `stratis-cli` | `sources/block-storage/stratis-cli` | https://github.com/stratis-storage/stratis-cli.git | yes | Stratis CLI and D-Bus flow. |
| important | `stratisd` | `sources/block-storage/stratisd` | https://github.com/stratis-storage/stratisd.git | yes | Stratis storage daemon over dm and XFS. |
| important | `util-linux` | `sources/block-storage/util-linux` | https://github.com/util-linux/util-linux.git | yes | mount umount findmnt libmount libblkid losetup fsck wrapper and block utilities. |
| important | `vdo` | `sources/block-storage/vdo` | https://github.com/dm-vdo/vdo.git | yes | VDO userspace format and stats tools. |
| adjacent | `devicemapper-rs` | `sources/block-storage/devicemapper-rs` | https://github.com/stratis-storage/devicemapper-rs.git | no | Rust device-mapper bindings used by Stratis. |
| adjacent | `libblkid-rs` | `sources/block-storage/libblkid-rs` | https://github.com/stratis-storage/libblkid-rs.git | no | Rust libblkid bindings used by Stratis. |
| adjacent | `libcryptsetup-rs` | `sources/block-storage/libcryptsetup-rs` | https://github.com/stratis-storage/libcryptsetup-rs.git | no | Rust libcryptsetup bindings used by Stratis. |

### cloud-native

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `containerd` | `sources/cloud-native/containerd` | https://github.com/containerd/containerd.git | yes | Snapshotter interfaces and overlay/native storage paths. |
| required | `containers-storage` | `sources/cloud-native/containers-storage` | https://github.com/containers/storage.git | yes | Container storage graph drivers and layer metadata. |
| required | `fuse-overlayfs` | `sources/cloud-native/fuse-overlayfs` | https://github.com/containers/fuse-overlayfs.git | yes | FUSE implementation of overlay semantics. |
| required | `ostree` | `sources/cloud-native/ostree` | https://github.com/ostreedev/ostree.git | yes | Content-addressed filesystem tree deployment. |
| important | `composefs` | `sources/cloud-native/composefs` | https://github.com/composefs/composefs.git | yes | Composable content-addressed filesystem images. |
| important | `composefs-rs` | `sources/cloud-native/composefs-rs` | https://github.com/composefs/composefs-rs.git | yes | Rust composefs tooling and library source. |
| important | `fuse-overlayfs-snapshotter` | `sources/cloud-native/fuse-overlayfs-snapshotter` | https://github.com/containerd/fuse-overlayfs-snapshotter.git | yes | containerd snapshotter integration for fuse-overlayfs. |
| important | `nydus` | `sources/cloud-native/nydus` | https://github.com/dragonflyoss/nydus.git | yes | Lazy image filesystem and RAFS implementation. |
| important | `nydus-snapshotter` | `sources/cloud-native/nydus-snapshotter` | https://github.com/containerd/nydus-snapshotter.git | yes | containerd snapshotter integration for Nydus. |
| important | `overlayfs-tools` | `sources/cloud-native/overlayfs-tools` | https://github.com/kmxz/overlayfs-tools.git | yes | OverlayFS inspection and debugging tools. |
| important | `soci-snapshotter` | `sources/cloud-native/soci-snapshotter` | https://github.com/awslabs/soci-snapshotter.git | yes | Seekable OCI snapshotter source. |
| important | `stargz-snapshotter` | `sources/cloud-native/stargz-snapshotter` | https://github.com/containerd/stargz-snapshotter.git | yes | Lazy-pull eStargz filesystem/snapshotter. |
| adjacent | `buildkit` | `sources/cloud-native/buildkit` | https://github.com/moby/buildkit.git | no | Build cache snapshot and content store source. |
| adjacent | `cri-o` | `sources/cloud-native/cri-o` | https://github.com/cri-o/cri-o.git | no | CRI-O rootfs and container storage integration source. |
| adjacent | `moby` | `sources/cloud-native/moby` | https://github.com/moby/moby.git | no | Docker graphdriver and overlay2 integration source. |
| adjacent | `overlaybd` | `sources/cloud-native/overlaybd` | https://github.com/containerd/overlaybd.git | no | Block-based remote image snapshotter source. |

### compression

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| adjacent | `lz4` | `sources/compression/lz4` | https://github.com/lz4/lz4.git | no | LZ4 compression source. |
| adjacent | `xz` | `sources/compression/xz` | https://github.com/tukaani-project/xz.git | no | XZ/LZMA compression source. |
| adjacent | `zlib` | `sources/compression/zlib` | https://github.com/madler/zlib.git | no | zlib compression source. |
| adjacent | `zstd` | `sources/compression/zstd` | https://github.com/facebook/zstd.git | no | Compression engine used by filesystems and backup tools. |

### control-plane

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| important | `beegfs-csi-driver` | `sources/control-plane/beegfs-csi-driver` | https://github.com/ThinkParQ/beegfs-csi-driver.git | yes | BeeGFS CSI driver source. |
| important | `ceph-csi` | `sources/control-plane/ceph-csi` | https://github.com/ceph/ceph-csi.git | yes | CephFS/RBD CSI provisioning mount snapshot source. |
| important | `csi-driver-iscsi` | `sources/control-plane/csi-driver-iscsi` | https://github.com/kubernetes-csi/csi-driver-iscsi.git | no | iSCSI CSI driver source for block-backed filesystem study. |
| important | `csi-driver-nfs` | `sources/control-plane/csi-driver-nfs` | https://github.com/kubernetes-csi/csi-driver-nfs.git | no | NFS CSI driver source. |
| important | `csi-driver-smb` | `sources/control-plane/csi-driver-smb` | https://github.com/kubernetes-csi/csi-driver-smb.git | no | SMB CSI driver source. |
| important | `csi-spec` | `sources/control-plane/csi-spec` | https://github.com/container-storage-interface/spec.git | no | CSI protobuf/interface source for direct storage drivers. |
| important | `juicefs-csi-driver` | `sources/control-plane/juicefs-csi-driver` | https://github.com/juicedata/juicefs-csi-driver.git | yes | JuiceFS CSI driver source. |
| important | `longhorn` | `sources/control-plane/longhorn` | https://github.com/longhorn/longhorn.git | yes | Kubernetes distributed block storage source for FS-on-distributed-block study. |
| important | `longhorn-engine` | `sources/control-plane/longhorn-engine` | https://github.com/longhorn/longhorn-engine.git | no | Longhorn replicated block engine source. |
| important | `mayastor` | `sources/control-plane/mayastor` | https://github.com/openebs/mayastor.git | no | SPDK-backed Kubernetes storage engine and CSI data-path source. |
| important | `rook` | `sources/control-plane/rook` | https://github.com/rook/rook.git | yes | CephFS/RBD Kubernetes operator and orchestration source. |
| adjacent | `csi-driver-host-path` | `sources/control-plane/csi-driver-host-path` | https://github.com/kubernetes-csi/csi-driver-host-path.git | no | Reference CSI hostpath driver. |
| adjacent | `csi-lib-utils` | `sources/control-plane/csi-lib-utils` | https://github.com/kubernetes-csi/csi-lib-utils.git | no | CSI shared utility source. |
| adjacent | `external-snapshotter` | `sources/control-plane/external-snapshotter` | https://github.com/kubernetes-csi/external-snapshotter.git | no | CSI snapshot sidecar source. |

### cow-pools

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `bcachefs` | `sources/cow-pools/bcachefs` | https://github.com/koverstreet/bcachefs.git | yes | bcachefs filesystem kernel source mirror. |
| required | `bcachefs-tools` | `sources/cow-pools/bcachefs-tools` | https://github.com/koverstreet/bcachefs-tools.git | yes | bcachefs mkfs fsck mount and tooling. |
| required | `nilfs-utils` | `sources/cow-pools/nilfs-utils` | https://github.com/nilfs-dev/nilfs-utils.git | yes | NILFS continuous snapshot userspace tools. |
| required | `openzfs` | `sources/cow-pools/openzfs` | https://github.com/openzfs/zfs.git | yes | ZFS core pool checksum COW snapshot and platform glue. |
| important | `nilfs2-kmod10` | `sources/cow-pools/nilfs2-kmod10` | https://github.com/nilfs-dev/nilfs2-kmod10.git | no | Standalone NILFS2 module for enterprise kernel contrast. |

### distributed-fs

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `alluxio` | `sources/distributed-fs/alluxio` | https://github.com/Alluxio/alluxio.git | yes | Virtual distributed filesystem and cache layer. |
| required | `beegfs` | `sources/distributed-fs/beegfs` | https://github.com/ThinkParQ/beegfs.git | yes | BeeGFS C/C++ metadata storage client module fsck. |
| required | `ceph` | `sources/distributed-fs/ceph` | https://github.com/ceph/ceph.git | yes | CephFS MDS clients RADOS OSD MON and RGW context. |
| required | `glusterfs` | `sources/distributed-fs/glusterfs` | https://github.com/gluster/glusterfs.git | yes | GlusterFS translators RPC daemons and FUSE/native clients. |
| required | `hadoop` | `sources/distributed-fs/hadoop` | https://gitbox.apache.org/repos/asf/hadoop.git | yes | HDFS and shared Hadoop storage/client code. |
| required | `juicefs` | `sources/distributed-fs/juicefs` | https://github.com/juicedata/juicefs.git | yes | POSIX filesystem over metadata DB and object storage. |
| required | `lustre-release` | `sources/distributed-fs/lustre-release` | https://github.com/lustre/lustre-release.git | yes | Lustre client server LNet ptlrpc MDT OST LLite source. |
| required | `moosefs` | `sources/distributed-fs/moosefs` | https://github.com/moosefs/moosefs.git | yes | MooseFS master chunkserver client implementation. |
| required | `seaweedfs` | `sources/distributed-fs/seaweedfs` | https://github.com/seaweedfs/seaweedfs.git | yes | Filer volume server S3 gateway and filesystem mount. |
| important | `beegfs-go` | `sources/distributed-fs/beegfs-go` | https://github.com/ThinkParQ/beegfs-go.git | yes | BeeGFS Go CLI and management libraries. |
| important | `beegfs-protobuf` | `sources/distributed-fs/beegfs-protobuf` | https://github.com/ThinkParQ/protobuf.git | no | BeeGFS protocol definitions. |
| important | `beegfs-rust` | `sources/distributed-fs/beegfs-rust` | https://github.com/ThinkParQ/beegfs-rust.git | yes | BeeGFS newer Rust management components. |
| important | `ceph-client` | `sources/distributed-fs/ceph-client` | https://github.com/ceph/ceph-client.git | no | Ceph kernel client standalone mirror. |
| important | `coda` | `sources/distributed-fs/coda` | https://github.com/cmusatyalab/coda.git | yes | Coda disconnected operation distributed filesystem. |
| important | `eos` | `sources/distributed-fs/eos` | https://gitlab.cern.ch/dss/eos.git | yes | CERN EOS distributed disk storage and namespace. |
| important | `lizardfs` | `sources/distributed-fs/lizardfs` | https://github.com/lizardfs/lizardfs.git | yes | MooseFS-family distributed filesystem fork. |
| important | `openafs` | `sources/distributed-fs/openafs` | https://github.com/openafs/openafs.git | yes | AFS distributed filesystem implementation. |
| important | `orangefs` | `sources/distributed-fs/orangefs` | https://github.com/waltligon/orangefs.git | yes | OrangeFS/PVFS parallel filesystem source. |
| important | `xrootd` | `sources/distributed-fs/xrootd` | https://github.com/xrootd/xrootd.git | yes | XRootD storage federation and file access. |
| adjacent | `ipfs-kubo` | `sources/distributed-fs/ipfs-kubo` | https://github.com/ipfs/kubo.git | no | Content-addressed distributed file graph; not POSIX. |
| adjacent | `tahoe-lafs` | `sources/distributed-fs/tahoe-lafs` | https://github.com/tahoe-lafs/tahoe-lafs.git | no | Capability-secure distributed filesystem. |

### local-fs

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `btrfs-progs` | `sources/local-fs/btrfs-progs` | https://github.com/kdave/btrfs-progs.git | yes | Btrfs mkfs check send receive inspect and libbtrfsutil. |
| required | `dosfstools` | `sources/local-fs/dosfstools` | https://github.com/dosfstools/dosfstools.git | yes | FAT mkfs fsck userspace. |
| required | `e2fsprogs` | `sources/local-fs/e2fsprogs` | https://git.kernel.org/pub/scm/fs/ext2/e2fsprogs.git | yes | ext2 ext3 ext4 mkfs fsck debugfs libraries. |
| required | `erofs-utils` | `sources/local-fs/erofs-utils` | https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git | yes | EROFS mkfs fsck dump and compressed read-only image tooling. |
| required | `exfatprogs` | `sources/local-fs/exfatprogs` | https://github.com/exfatprogs/exfatprogs.git | yes | exFAT mkfs fsck dump tune label tooling. |
| required | `f2fs-tools` | `sources/local-fs/f2fs-tools` | https://git.kernel.org/pub/scm/linux/kernel/git/jaegeuk/f2fs-tools.git | yes | F2FS mkfs fsck dump resize and sparse mobile-flash tooling. |
| required | `ntfs-3g` | `sources/local-fs/ntfs-3g` | https://github.com/tuxera/ntfs-3g.git | yes | NTFS userspace driver and ntfsprogs source. |
| required | `xfsprogs` | `sources/local-fs/xfsprogs` | https://git.kernel.org/pub/scm/fs/xfs/xfsprogs-dev.git | yes | XFS userspace repair mkfs grow quota and libraries. |
| important | `btrfs-linux` | `sources/local-fs/btrfs-linux` | https://github.com/btrfs/linux.git | yes | Btrfs development kernel tree for in-flight fs/btrfs work. |
| important | `dlm` | `sources/local-fs/dlm` | https://pagure.io/dlm.git | no | Distributed lock manager userspace for cluster filesystems. |
| important | `gfs2-utils` | `sources/local-fs/gfs2-utils` | https://pagure.io/gfs2-utils.git | yes | GFS2 cluster filesystem userspace tools. |
| important | `jfsutils` | `sources/local-fs/jfsutils` | https://github.com/SudoMaker/jfsutils.git | yes | JFS fsck mkfs logdump and utilities; public Git mirror, canonical source should be rechecked. |
| important | `kdave-linux` | `sources/local-fs/kdave-linux` | https://git.kernel.org/pub/scm/linux/kernel/git/kdave/linux.git | no | Btrfs maintainer integration tree; can stay deferred if LOC is high. |
| important | `mtd-utils` | `sources/local-fs/mtd-utils` | https://git.kernel.org/pub/scm/linux/kernel/git/rw/mtd-utils.git | yes | MTD UBI UBIFS JFFS2 userspace tools. |
| important | `ocfs2-tools` | `sources/local-fs/ocfs2-tools` | https://github.com/markfasheh/ocfs2-tools.git | yes | OCFS2 cluster filesystem userspace tools. |
| important | `squashfs-tools` | `sources/local-fs/squashfs-tools` | https://github.com/plougher/squashfs-tools.git | yes | SquashFS image creation extraction and compression paths. |
| important | `udftools` | `sources/local-fs/udftools` | https://github.com/pali/udftools.git | yes | UDF filesystem userspace tools. |
| important | `xfsdump` | `sources/local-fs/xfsdump` | https://git.kernel.org/pub/scm/fs/xfs/xfsdump-dev.git | yes | XFS dump restore and incremental backup source. |
| adjacent | `apfs-fuse` | `sources/local-fs/apfs-fuse` | https://github.com/sgan81/apfs-fuse.git | no | Public APFS reverse-engineered FUSE reader. |
| adjacent | `linux-apfs-rw` | `sources/local-fs/linux-apfs-rw` | https://github.com/linux-apfs/linux-apfs-rw.git | no | Public Linux APFS read/write implementation. |
| adjacent | `reiserfsprogs` | `sources/local-fs/reiserfsprogs` | https://git.kernel.org/pub/scm/linux/kernel/git/jeffm/reiserfsprogs.git | no | Historical tree filesystem userspace. |

### object-store

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `apache-ozone` | `sources/object-store/apache-ozone` | https://github.com/apache/ozone.git | yes | Hadoop object store and Ozone Manager/DataNode code. |
| required | `daos` | `sources/object-store/daos` | https://github.com/daos-stack/daos.git | yes | HPC distributed object store and VOS engine. |
| required | `minio` | `sources/object-store/minio` | https://github.com/minio/minio.git | yes | S3-compatible object storage source; track maintenance caveat. |
| required | `openstack-swift` | `sources/object-store/openstack-swift` | https://opendev.org/openstack/swift.git | yes | OpenStack Swift distributed object storage canonical source. |
| important | `garage` | `sources/object-store/garage` | https://git.deuxfleurs.fr/Deuxfleurs/garage.git | yes | Geo-distributed S3-compatible object store. |
| important | `minio-mc` | `sources/object-store/minio-mc` | https://github.com/minio/mc.git | yes | S3/minio file-style client and mirror/diff/admin flows. |
| important | `rustfs` | `sources/object-store/rustfs` | https://github.com/rustfs/rustfs.git | yes | Rust S3-compatible object storage implementation. |

### os-vfs

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `dragonflybsd` | `sources/os/bsd/dragonflybsd` | https://github.com/DragonFlyBSD/DragonFlyBSD.git | yes | HAMMER HAMMER2 vnode and BSD VFS contrast. |
| required | `freebsd-src` | `sources/os/bsd/freebsd-src` | https://git.FreeBSD.org/src.git | yes | FreeBSD VFS UFS ZFS FUSE and filesystem tools. |
| required | `illumos-gate` | `sources/os/illumos/illumos-gate` | https://github.com/illumos/illumos-gate.git | yes | Solaris VFS vnode ZFS NFS UFS tmpfs lineage. |
| required | `linux` | `sources/os/linux/linux` | https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git | yes | VFS page-cache block layer and in-kernel local/network filesystems. |
| required | `netbsd-src` | `sources/os/bsd/netbsd-src` | https://github.com/NetBSD/src.git | yes | NetBSD VFS PUFFS refuse rump and historical ZFS port. |
| required | `openbsd-src` | `sources/os/bsd/openbsd-src` | https://github.com/openbsd/src.git | yes | OpenBSD VFS FFS UFS FUSE and security-oriented FS paths. |
| important | `9front` | `sources/os/plan9/9front` | https://github.com/9front/9front.git | yes | Actively maintained Plan 9 derivative and 9P/fossil contrast. |
| important | `linux-stable` | `sources/os/linux/linux-stable` | https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git | no | Stable backport context for filesystem fixes. |
| important | `plan9` | `sources/os/plan9/plan9` | https://github.com/plan9foundation/plan9.git | yes | Namespace 9P fossil venti and lib9p source model. |
| important | `xnu` | `sources/os/darwin/xnu` | https://github.com/apple-oss-distributions/xnu.git | yes | Public Darwin/XNU VFS and filesystem source. |

### security-integrity

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `fscrypt` | `sources/security-integrity/fscrypt` | https://github.com/google/fscrypt.git | yes | Linux filesystem encryption userspace. |
| required | `fsverity-utils` | `sources/security-integrity/fsverity-utils` | https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git | yes | fs-verity userspace signing and measurement tools. |
| important | `acl` | `sources/security-integrity/acl` | https://git.savannah.nongnu.org/git/acl.git | yes | POSIX ACL userspace library and tools. |
| important | `attr` | `sources/security-integrity/attr` | https://git.savannah.nongnu.org/git/attr.git | yes | Extended attributes library and tools. |
| important | `audit-userspace` | `sources/security-integrity/audit-userspace` | https://github.com/linux-audit/audit-userspace.git | yes | Audit userspace for file access and security event semantics. |
| important | `cryfs` | `sources/security-integrity/cryfs` | https://github.com/cryfs/cryfs.git | yes | Encrypted cloud-oriented FUSE filesystem. |
| important | `ecryptfs-utils` | `sources/security-integrity/ecryptfs-utils` | https://github.com/dustinkirkland/ecryptfs-utils.git | yes | eCryptfs userspace utilities. |
| important | `encfs` | `sources/security-integrity/encfs` | https://github.com/vgough/encfs.git | yes | Historical encrypted FUSE filesystem. |
| important | `gocryptfs` | `sources/security-integrity/gocryptfs` | https://github.com/rfjakob/gocryptfs.git | yes | Encrypted FUSE filesystem. |
| important | `ima-evm-utils` | `sources/security-integrity/ima-evm-utils` | https://github.com/linux-integrity/ima-evm-utils.git | yes | Linux IMA/EVM file integrity userspace. |
| important | `keyutils` | `sources/security-integrity/keyutils` | https://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git | yes | Linux key retention service userspace. |
| important | `libcap` | `sources/security-integrity/libcap` | https://git.kernel.org/pub/scm/libs/libcap/libcap.git | yes | Linux file capabilities and capability utilities. |
| important | `selinux` | `sources/security-integrity/selinux` | https://github.com/SELinuxProject/selinux.git | yes | SELinux labels policy loading and file context source. |

### storage-engines

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| adjacent | `badger` | `sources/storage-engines/badger` | https://github.com/dgraph-io/badger.git | no | LSM/value-log source. |
| adjacent | `foundationdb` | `sources/storage-engines/foundationdb` | https://github.com/apple/foundationdb.git | no | Distributed storage engine and transaction log source. |
| adjacent | `leveldb` | `sources/storage-engines/leveldb` | https://github.com/google/leveldb.git | no | Minimal LSM design reference. |
| adjacent | `lmdb` | `sources/storage-engines/lmdb` | https://github.com/LMDB/lmdb.git | no | Mmap B+tree storage engine source. |
| adjacent | `pebble` | `sources/storage-engines/pebble` | https://github.com/cockroachdb/pebble.git | no | Go LSM engine and manifest/WAL implementation. |
| adjacent | `raft-engine` | `sources/storage-engines/raft-engine` | https://github.com/tikv/raft-engine.git | no | TiKV standalone raft log engine with file-pipe log storage. |
| adjacent | `rocksdb` | `sources/storage-engines/rocksdb` | https://github.com/facebook/rocksdb.git | no | LSM storage engine used for metadata and object-store comparisons. |
| adjacent | `sqlite` | `sources/storage-engines/sqlite` | https://github.com/sqlite/sqlite.git | no | Pager VFS WAL and btree source mirror. |
| adjacent | `tikv` | `sources/storage-engines/tikv` | https://github.com/tikv/tikv.git | no | Distributed Raft/LSM storage engine. |
| adjacent | `wiredtiger` | `sources/storage-engines/wiredtiger` | https://github.com/wiredtiger/wiredtiger.git | no | B-tree/log/checkpoint storage engine. |

### sync-backup

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `rsync` | `sources/sync-backup/rsync` | https://github.com/RsyncProject/rsync.git | yes | File-tree delta transfer and metadata preservation. |
| required | `syncthing` | `sources/sync-backup/syncthing` | https://github.com/syncthing/syncthing.git | yes | Distributed file synchronization semantics. |
| important | `borg` | `sources/sync-backup/borg` | https://github.com/borgbackup/borg.git | yes | Deduplicating encrypted backup filesystem-like repository. |
| important | `casync` | `sources/sync-backup/casync` | https://github.com/systemd/casync.git | no | Content-addressed synchronization source. |
| important | `git-annex` | `sources/sync-backup/git-annex` | https://git.joeyh.name/git/git-annex.git | yes | File tree indirection and distributed content management. |
| important | `git-crypt` | `sources/sync-backup/git-crypt` | https://github.com/AGWA/git-crypt.git | no | Transparent Git file encryption source. |
| important | `git-lfs` | `sources/sync-backup/git-lfs` | https://github.com/git-lfs/git-lfs.git | yes | Git large-file pointer and content transfer semantics. |
| important | `kopia` | `sources/sync-backup/kopia` | https://github.com/kopia/kopia.git | yes | Content-addressed backup and snapshot source. |
| important | `restic` | `sources/sync-backup/restic` | https://github.com/restic/restic.git | yes | Content-addressed backup repository source. |
| important | `unison` | `sources/sync-backup/unison` | https://github.com/bcpierce00/unison.git | yes | Bidirectional file tree reconciliation source. |
| adjacent | `bup` | `sources/sync-backup/bup` | https://github.com/bup/bup.git | no | Git-pack based backup source. |

### teaching

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| important | `minix` | `sources/teaching/minix` | https://github.com/Stichting-MINIX-Research-Foundation/minix.git | yes | Microkernel VFS servers filesystem servers and storage drivers. |
| important | `os161` | `sources/teaching/os161` | https://github.com/ops-class/os161.git | yes | Teaching VFS structure closer to production OSes than xv6. |
| important | `xv6-public` | `sources/teaching/xv6-public` | https://github.com/mit-pdos/xv6-public.git | yes | Historical xv6 x86 filesystem implementation. |
| important | `xv6-riscv` | `sources/teaching/xv6-riscv` | https://github.com/mit-pdos/xv6-riscv.git | yes | Minimal inode log buffer-cache and file syscall implementation. |
| adjacent | `pintos` | `sources/teaching/pintos` | https://github.com/fghanei/pintos.git | no | Teaching file system project baseline; exclude student solution forks. |

### test-tools

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `blktests` | `sources/test-tools/blktests` | https://github.com/osandov/blktests.git | yes | Block layer and NVMe regression tests. |
| required | `fio` | `sources/test-tools/fio` | https://github.com/axboe/fio.git | yes | Filesystem and block I/O workload generator source. |
| required | `ltp` | `sources/test-tools/ltp` | https://github.com/linux-test-project/ltp.git | yes | Linux syscall/fs stress and conformance tests. |
| required | `xfstests` | `sources/test-tools/xfstests` | https://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git | yes | Filesystem regression tests fsstress fsx and generic FS coverage. |
| important | `crashmonkey` | `sources/test-tools/crashmonkey` | https://github.com/utsaslab/crashmonkey.git | no | Crash-consistency testing source. |
| important | `cthon04` | `sources/test-tools/cthon04` | https://github.com/phdeniel/cthon04.git | no | Legacy NFS interoperability tests. |
| important | `filebench` | `sources/test-tools/filebench` | https://github.com/filebench/filebench.git | no | Filesystem workload benchmark source. |
| important | `fs-mark` | `sources/test-tools/fs-mark` | https://github.com/josefbacik/fs_mark.git | no | Metadata benchmark source. |
| important | `ior` | `sources/test-tools/ior` | https://github.com/hpc/ior.git | no | HPC parallel I/O benchmark source. |
| important | `iozone` | `sources/test-tools/iozone` | https://github.com/pantheon-systems/iozone.git | no | Filesystem benchmark source; public Git mirror. |
| important | `kdevops` | `sources/test-tools/kdevops` | https://github.com/linux-kdevops/kdevops.git | no | Kernel and filesystem test automation source. |
| important | `lcov` | `sources/test-tools/lcov` | https://github.com/linux-test-project/lcov.git | no | Coverage tooling source. |
| important | `liburing` | `sources/test-tools/liburing` | https://github.com/axboe/liburing.git | no | io_uring library and tests. |
| important | `pjdfstest` | `sources/test-tools/pjdfstest` | https://github.com/pjd/pjdfstest.git | yes | POSIX filesystem behavior tests. |
| important | `pynfs` | `sources/test-tools/pynfs` | https://github.com/linux-nfs/pynfs.git | no | NFSv4 protocol tests. |
| important | `strace` | `sources/test-tools/strace` | https://github.com/strace/strace.git | no | Syscall tracing source useful for VFS behavior observation. |
| important | `stress-ng` | `sources/test-tools/stress-ng` | https://github.com/ColinIanKing/stress-ng.git | no | Stress workload source with filesystem stressors. |
| important | `unionmount-testsuite` | `sources/test-tools/unionmount-testsuite` | https://github.com/amir73il/unionmount-testsuite.git | no | Overlay/union mount behavior tests. |
| important | `xfstests-bld` | `sources/test-tools/xfstests-bld` | https://github.com/tytso/xfstests-bld.git | no | xfstests automation and VM flows. |
| adjacent | `syzkaller` | `sources/test-tools/syzkaller` | https://github.com/google/syzkaller.git | no | Kernel fuzzing source with filesystem bug-finding value. |

### user-network-fs

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `cifs-utils` | `sources/user-network-fs/cifs-utils` | https://git.samba.org/cifs-utils.git | yes | Linux CIFS mount tools. |
| required | `libfuse` | `sources/user-network-fs/libfuse` | https://github.com/libfuse/libfuse.git | yes | FUSE protocol library examples and mount utilities. |
| required | `nfs-ganesha` | `sources/user-network-fs/nfs-ganesha` | https://github.com/nfs-ganesha/nfs-ganesha.git | yes | User-space NFS server and FSAL architecture. |
| required | `nfs-utils` | `sources/user-network-fs/nfs-utils` | https://github.com/linux-nfs/nfs-utils.git | yes | Linux NFS mountd statd idmapd and client/server utilities. |
| required | `samba` | `sources/user-network-fs/samba` | https://github.com/samba-team/samba.git | yes | SMB/CIFS server client VFS modules and protocol stack. |
| required | `sshfs` | `sources/user-network-fs/sshfs` | https://github.com/libfuse/sshfs.git | yes | FUSE filesystem over SFTP. |
| important | `bazil-fuse` | `sources/user-network-fs/bazil-fuse` | https://github.com/bazil/fuse.git | yes | Go FUSE implementation used by several userfs projects. |
| important | `blobfuse2` | `sources/user-network-fs/blobfuse2` | https://github.com/Azure/azure-storage-fuse.git | yes | Azure Storage FUSE implementation. |
| important | `davfs2` | `sources/user-network-fs/davfs2` | https://github.com/alisarctl/davfs2.git | yes | WebDAV filesystem mount implementation. |
| important | `fusepy` | `sources/user-network-fs/fusepy` | https://github.com/fusepy/fusepy.git | no | Small Python FUSE binding for API contrast. |
| important | `gcsfuse` | `sources/user-network-fs/gcsfuse` | https://github.com/GoogleCloudPlatform/gcsfuse.git | yes | Google Cloud Storage FUSE implementation. |
| important | `go-fuse` | `sources/user-network-fs/go-fuse` | https://github.com/hanwen/go-fuse.git | yes | Go FUSE implementation and examples. |
| important | `impacket` | `sources/user-network-fs/impacket` | https://github.com/fortra/impacket.git | yes | Python SMB/RPC protocol implementation useful for packet-level study. |
| important | `ksmbd-tools` | `sources/user-network-fs/ksmbd-tools` | https://github.com/cifsd-team/ksmbd-tools.git | yes | Userspace tools for in-kernel SMB server. |
| important | `libnfs` | `sources/user-network-fs/libnfs` | https://github.com/sahlberg/libnfs.git | yes | User-space NFS client library. |
| important | `libsmb2` | `sources/user-network-fs/libsmb2` | https://github.com/sahlberg/libsmb2.git | yes | Compact SMB2/3 client library. |
| important | `libtirpc` | `sources/user-network-fs/libtirpc` | git://linux-nfs.org/~steved/libtirpc | no | TIRPC dependency source for NFS userspace closure. |
| important | `macfuse` | `sources/user-network-fs/macfuse` | https://github.com/macfuse/macfuse.git | yes | Public macOS FUSE implementation. |
| important | `mergerfs` | `sources/user-network-fs/mergerfs` | https://github.com/trapexit/mergerfs.git | yes | Policy-heavy FUSE union filesystem. |
| important | `pyfuse3` | `sources/user-network-fs/pyfuse3` | https://github.com/libfuse/pyfuse3.git | yes | Python FUSE binding and examples. |
| important | `rpcbind` | `sources/user-network-fs/rpcbind` | git://linux-nfs.org/~steved/rpcbind | no | RPC bind service source for NFS userspace closure. |
| important | `s3fs-fuse` | `sources/user-network-fs/s3fs-fuse` | https://github.com/s3fs-fuse/s3fs-fuse.git | yes | S3 object-store filesystem via FUSE. |
| adjacent | `go-nfs` | `sources/user-network-fs/go-nfs` | https://github.com/willscott/go-nfs.git | no | Small Go NFS server/library for protocol reading. |
| adjacent | `rclone` | `sources/user-network-fs/rclone` | https://github.com/rclone/rclone.git | no | Cloud storage FUSE/mount semantics and sync engine. |
| adjacent | `smbj` | `sources/user-network-fs/smbj` | https://github.com/hierynomus/smbj.git | no | Java SMB2/3 client implementation. |
| adjacent | `smblibrary` | `sources/user-network-fs/smblibrary` | https://github.com/TalAloni/SMBLibrary.git | no | C# SMB client/server implementation. |

### virtualization

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `qemu` | `sources/virtualization/qemu` | https://gitlab.com/qemu-project/qemu.git | yes | Block layer qcow2 NBD virtiofs historical source. |
| required | `spdk` | `sources/virtualization/spdk` | https://github.com/spdk/spdk.git | yes | User-space NVMe/blobstore/block storage stack. |
| important | `guestfs-tools` | `sources/virtualization/guestfs-tools` | https://github.com/libguestfs/guestfs-tools.git | yes | Guest filesystem image tools. |
| important | `libblockdev` | `sources/virtualization/libblockdev` | https://github.com/storaged-project/libblockdev.git | yes | Block-device operation library. |
| important | `libguestfs` | `sources/virtualization/libguestfs` | https://github.com/libguestfs/libguestfs.git | yes | Guest filesystem image inspection and modification source. |
| important | `libnbd` | `sources/virtualization/libnbd` | https://gitlab.com/nbdkit/libnbd.git | yes | NBD client library and tooling. |
| important | `nbd` | `sources/virtualization/nbd` | https://github.com/NetworkBlockDevice/nbd.git | yes | NBD client/server source. |
| important | `nbdkit` | `sources/virtualization/nbdkit` | https://gitlab.com/nbdkit/nbdkit.git | yes | NBD server plugins and filters. |
| important | `nvme-cli` | `sources/virtualization/nvme-cli` | https://github.com/linux-nvme/nvme-cli.git | yes | NVMe admin and test tooling. |
| important | `open-iscsi` | `sources/virtualization/open-iscsi` | https://github.com/open-iscsi/open-iscsi.git | no | iSCSI block-storage path adjacent to remote FS. |
| important | `virtiofsd` | `sources/virtualization/virtiofsd` | https://gitlab.com/virtio-fs/virtiofsd.git | yes | Standalone virtiofs daemon if upstream remains available. |

### windows-public

| Tier | ID | Local path | Upstream | Default count | Notes |
|---|---|---|---|---|---|
| required | `dokany` | `sources/windows/dokany` | https://github.com/dokan-dev/dokany.git | yes | Windows FUSE-like filesystem driver and library. |
| required | `reactos` | `sources/windows/reactos` | https://github.com/reactos/reactos.git | yes | Public NT-like FS and IO manager implementation. |
| required | `winbtrfs` | `sources/windows/winbtrfs` | https://github.com/maharmstone/btrfs.git | yes | Public Windows Btrfs driver implementation. |
| required | `winfsp` | `sources/windows/winfsp` | https://github.com/winfsp/winfsp.git | yes | Windows user-mode filesystem framework and FUSE bridge. |
| important | `windows-driver-samples` | `sources/windows/windows-driver-samples` | https://github.com/microsoft/Windows-driver-samples.git | yes | Public filesystem and minifilter samples only. |

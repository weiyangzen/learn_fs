# Agent 09 Source Plan: Security, Integrity, Sync, Backup, Versioned Trees

Generated: 2026-06-15

This is Agent 09's candidate source-only slice for `/Users/wangweiyang/GitHub/learn_fs`.
The slice focuses on filesystem and distributed-file-tree semantics where security,
encryption, integrity, permissions, compression, backup/sync, or versioned trees are
implemented in source code.

The goal is not to collect every backup application. A project belongs here only if
its code teaches something about file trees: names, metadata, xattrs, hard links,
snapshots, content addressing, chunking, deduplication, encryption at rest,
verification, permissions, reconciliation, or reproducible tree deployment.

## Collection Boundary

- **Must collect source** for kernel implementations, userspace tools, FUSE
  encrypted filesystems, deduplicating encrypted backup engines, sync engines,
  content-addressed/versioned tree stores, and permission/integrity primitives.
- **May collect source** for adjacent compression, archive, remote transport, and
  historical projects when they clarify a design lineage or format.
- **Exclude** proprietary clients, SaaS control planes, binary-only backup agents,
  generic cloud sync GUIs, and backup wrappers that only schedule/call another tool
  without owning tree, chunk, integrity, or metadata semantics.
- **Prefer canonical upstreams** over distro mirrors. Distro packaging belongs in a
  separate packaging slice unless it carries meaningful patches for filesystem
  behavior.
- **Use case-sensitive storage** for Linux kernel and large filesystem trees. Normal
  case-insensitive macOS APFS can produce false conflicts in kernel checkouts.

## Priority Legend

- **P0 / 必收**: necessary for this Agent 09 topic to be useful.
- **P1 / 强可选**: important comparative implementation or required support layer.
- **P2 / 可选**: useful for breadth, history, or one feature family, but can wait.
- **Excluded / 不收**: out of source-only or file-tree-semantics scope.

## Proposed Directory Structure

```text
learn_fs/
  sources/
    kernel-core/
      linux/
      fsverity-utils/
      fscrypt/
      xfstests/
      blktests/
    encrypted-fuse/
      encfs/
      gocryptfs/
      cryfs/
      securefs/
      libfuse/
    ecryptfs/
      ecryptfs-utils/
    encryption-keys/
      cryptsetup/
      keyutils/
      tpm2-tools/
      tpm2-tss/
      openssl/
      libsodium/
      libgcrypt/
    integrity-permissions/
      acl/
      attr/
      libcap/
      ima-evm-utils/
      selinux/
      audit-userspace/
    compression-readonly/
      squashfs-tools/
      erofs-utils/
      zstd/
      xz/
      lz4/
      zlib/
    cow-snapshots/
      btrfs-progs/
      zfs/
      stratisd/
      lvm2/
      snapper/
    backup-dedup-encrypted/
      borg/
      restic/
      kopia/
      duplicacy/
      duplicity/
      attic/
    sync-replication/
      syncthing/
      rsync/
      unison/
      rclone/
      csync/
    content-addressed-versioned/
      git/
      git-annex/
      ostree/
      casync/
      composefs/
      bup/
      git-lfs/
      git-crypt/
    distributed-filesystems-security/
      ceph/
      glusterfs/
      juicefs/
      seaweedfs/
      ipfs-kubo/
    tests-fuzzing/
      fstests/
      fsx/
      fio/
      fsverity-utils-tests/
  Docs/
    agent09-security-integrity-sync-source-plan.md
```

The final combined repository can flatten or rename these groups. The important
constraint is to keep implementation families separate enough that a reader can
compare, for example, `fscrypt` policy code against FUSE filename encryption,
or Borg chunk authentication against Restic/Kopia repository formats.

## P0 / 必收清单

| Local path | Upstream | Why it is mandatory |
|---|---|---|
| `sources/kernel-core/linux` | `https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git` | Authoritative implementation for `fs/crypto`, `fs/verity`, `fs/ecryptfs`, VFS permission checks, xattrs, IMA/EVM hooks, overlayfs, btrfs, erofs, squashfs, NFS/CIFS client semantics, idmapped mounts, and namespace-related security behavior. This is the single most important codebase for Agent 09. |
| `sources/kernel-core/fscrypt` | `https://github.com/google/fscrypt.git` | Userspace policy/key management for Linux native filesystem encryption. Essential companion to kernel `fs/crypto` and ext4/f2fs/ubifs encryption behavior. |
| `sources/kernel-core/fsverity-utils` | `https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git` | Userspace tooling and tests for Merkle-tree file authenticity; pairs with kernel `fs/verity`. |
| `sources/kernel-core/xfstests` | `https://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git` | Cross-filesystem regression tests. Required to understand edge cases for encryption, verity, reflinks, hard links, xattrs, rename, fsync, quota, and crash consistency. |
| `sources/encrypted-fuse/libfuse` | `https://github.com/libfuse/libfuse.git` | Core FUSE userspace/kernel boundary. Needed before reading EncFS/gocryptfs/CryFS correctness and attack surfaces. |
| `sources/encrypted-fuse/gocryptfs` | `https://github.com/rfjakob/gocryptfs.git` | Modern encrypted FUSE overlay with filename encryption, reverse mode, performance tradeoffs, and explicit threat model. |
| `sources/encrypted-fuse/cryfs` | `https://github.com/cryfs/cryfs.git` | Encrypted cloud-filesystem design with block abstraction intended to hide metadata better than simple file-per-file overlays. |
| `sources/encrypted-fuse/encfs` | `https://github.com/vgough/encfs.git` | Historically important encrypted FUSE filesystem. Keep for design lineage and known security pitfalls, not as a modern recommendation. |
| `sources/ecryptfs/ecryptfs-utils` | `https://code.launchpad.net/~ecryptfs/ecryptfs/trunk` | Userspace tools for stacked cryptographic filesystem history. Launchpad/Bazaar source is canonical; mirror only if Bazaar access becomes operationally painful. |
| `sources/backup-dedup-encrypted/borg` | `https://github.com/borgbackup/borg.git` | Deduplicating encrypted backup repository with chunk indexes, authenticated encryption, pruning, and archive metadata semantics. |
| `sources/backup-dedup-encrypted/restic` | `https://github.com/restic/restic.git` | Deduplicating encrypted backup repository with content-addressed packs, tree snapshots, and backend abstraction. Strong contrast to Borg. |
| `sources/backup-dedup-encrypted/kopia` | `https://github.com/kopia/kopia.git` | Modern dedup/encrypted snapshot engine with policies, content manager, manifests, and repository maintenance code. |
| `sources/sync-replication/syncthing` | `https://github.com/syncthing/syncthing.git` | Continuous bidirectional file synchronization with block exchange, versioning, conflict handling, ignore semantics, and device trust model. |
| `sources/sync-replication/rsync` | `https://git.samba.org/rsync.git` | Classic rolling-checksum file-tree synchronization. Mandatory baseline for delta transfer and metadata preservation. |
| `sources/content-addressed-versioned/git-annex` | `git://git-annex.branchable.com/` | Git-backed large-file tree management: content keys, remotes, availability tracking, sync/assistant modes, archival semantics. |
| `sources/content-addressed-versioned/ostree` | `https://github.com/ostreedev/ostree.git` | Content-addressed, versioned filesystem trees for OS deployment; commits, refs, static deltas, hardlink checkouts, integrity verification. |
| `sources/content-addressed-versioned/casync` | `https://github.com/systemd/casync.git` | Content-addressable synchronization/archive format; useful bridge between rsync-like delta transfer and tree/image deployment. |
| `sources/cow-snapshots/btrfs-progs` | `https://git.kernel.org/pub/scm/linux/kernel/git/kdave/btrfs-progs.git` | Userspace for btrfs subvolumes, send/receive, checksums, compression, snapshots, qgroups, scrub, and repair tooling. Kernel btrfs code is in Linux, but tools are needed for tree semantics. |
| `sources/cow-snapshots/zfs` | `https://github.com/openzfs/zfs.git` | OpenZFS source for checksums, compression, encryption, snapshots, send/receive, clones, dedup, ACLs, and dataset permissions. |
| `sources/compression-readonly/squashfs-tools` | `https://github.com/plougher/squashfs-tools.git` | Read-only compressed filesystem image creation/extraction; important for packed tree formats and initramfs/live systems. |
| `sources/compression-readonly/erofs-utils` | `https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git` | Modern read-only compressed filesystem tooling; compare with SquashFS and kernel EROFS. |
| `sources/integrity-permissions/acl` | `https://git.savannah.nongnu.org/git/acl.git` | POSIX ACL userspace tooling and libraries. |
| `sources/integrity-permissions/attr` | `https://git.savannah.nongnu.org/git/attr.git` | Extended attributes tooling and libraries; xattrs are central to ACLs, capabilities, encryption metadata, IMA/EVM, SELinux labels, and backup fidelity. |
| `sources/integrity-permissions/libcap` | `https://git.kernel.org/pub/scm/libs/libcap/libcap.git` | Linux file capabilities and process capability model, including xattr-backed file caps. |
| `sources/encryption-keys/keyutils` | `https://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git` | Linux key retention service userspace; important for eCryptfs, fscrypt, and kernel keyring flows. |
| `sources/encryption-keys/cryptsetup` | `https://gitlab.com/cryptsetup/cryptsetup.git` | LUKS/dm-crypt is block encryption rather than filesystem encryption, but it is the baseline boundary case every filesystem encryption design is compared against. |

## P1 / 强可选清单

| Local path | Upstream | Why it is useful |
|---|---|---|
| `sources/integrity-permissions/ima-evm-utils` | `https://git.kernel.org/pub/scm/linux/kernel/git/zohar/ima-evm-utils.git` | Userspace signing/verification helpers for Linux IMA/EVM file integrity and metadata protection. |
| `sources/integrity-permissions/selinux` | `https://github.com/SELinuxProject/selinux.git` | SELinux labels, policy loading, libselinux file contexts, and xattr-backed MAC semantics. |
| `sources/integrity-permissions/audit-userspace` | `https://github.com/linux-audit/audit-userspace.git` | Audit trail support for file access, permission, and security events. |
| `sources/compression-readonly/zstd` | `https://github.com/facebook/zstd.git` | Compression engine used by btrfs, SquashFS, EROFS, archives, and backup tools. |
| `sources/compression-readonly/xz` | `https://git.tukaani.org/xz.git` | LZMA/XZ compression used by filesystem images and archives. |
| `sources/compression-readonly/lz4` | `https://github.com/lz4/lz4.git` | Fast compression used in filesystems and backup tools. |
| `sources/compression-readonly/zlib` | `https://github.com/madler/zlib.git` | Baseline compression dependency used by older filesystems/tools. |
| `sources/sync-replication/unison` | `https://github.com/bcpierce00/unison.git` | Bidirectional sync with reconciliation logic distinct from Syncthing. Useful for conflict semantics. |
| `sources/sync-replication/rclone` | `https://github.com/rclone/rclone.git` | Optional backend/remote comparison. Include only when studying metadata loss across cloud object stores. |
| `sources/sync-replication/csync` | `https://github.com/owncloud/csync.git` | File tree reconciliation library used in cloud sync clients. Include for sync algorithm comparison, not for GUI clients. |
| `sources/content-addressed-versioned/git` | `https://github.com/git/git.git` | Required context for git-annex object/reference semantics and tree hashing. If already collected by another Agent, link rather than duplicate. |
| `sources/content-addressed-versioned/composefs` | `https://github.com/containers/composefs.git` | Image/tree composition with fs-verity integration; strong bridge between container images and verifiable filesystem trees. |
| `sources/content-addressed-versioned/bup` | `https://github.com/bup/bup.git` | Git-pack-based backup with rolling checksums. Useful contrast against Borg/Restic/Kopia. |
| `sources/content-addressed-versioned/git-lfs` | `https://github.com/git-lfs/git-lfs.git` | Large-file pointer semantics around Git. Less filesystem-like than git-annex but useful comparison. |
| `sources/content-addressed-versioned/git-crypt` | `https://github.com/AGWA/git-crypt.git` | Transparent Git file encryption. Include as a narrow encrypted-tree comparison. |
| `sources/backup-dedup-encrypted/duplicacy` | `https://github.com/gilbertchen/duplicacy.git` | Deduplicating backup with repository/chunk semantics. Some product pieces are commercial; collect only open source code. |
| `sources/backup-dedup-encrypted/duplicity` | `https://gitlab.com/duplicity/duplicity.git` | Encrypted incremental file-tree backup based on tar/GnuPG/rsync-like ideas. Include if studying historical backup formats. |
| `sources/backup-dedup-encrypted/attic` | `https://github.com/jborg/attic.git` | Borg predecessor. Useful for lineage, repository format evolution, and security hardening comparison. |
| `sources/cow-snapshots/stratisd` | `https://github.com/stratis-storage/stratisd.git` | Managed storage stack above LVM/XFS; useful when studying snapshot-oriented UX and policy code. |
| `sources/cow-snapshots/lvm2` | `https://sourceware.org/git/lvm2.git` | Snapshot/thin provisioning substrate. Block-level, but needed for boundary comparison with filesystem-level snapshots. |
| `sources/cow-snapshots/snapper` | `https://github.com/openSUSE/snapper.git` | Snapshot orchestration over btrfs/LVM with rollback policy. Include for user-visible versioning semantics. |
| `sources/encrypted-fuse/securefs` | `https://github.com/netheril96/securefs.git` | Additional encrypted FUSE implementation for design comparison. |
| `sources/encryption-keys/tpm2-tools` | `https://github.com/tpm2-software/tpm2-tools.git` | TPM-bound key management examples for encrypted storage workflows. |
| `sources/encryption-keys/tpm2-tss` | `https://github.com/tpm2-software/tpm2-tss.git` | TPM2 software stack dependency for hardware-backed storage secrets. |
| `sources/encryption-keys/openssl` | `https://github.com/openssl/openssl.git` | Crypto primitive implementation dependency for many tools. Include only if local disk budget allows or if auditing crypto calls. |
| `sources/encryption-keys/libsodium` | `https://github.com/jedisct1/libsodium.git` | Modern crypto library used by several storage/sync projects. |
| `sources/encryption-keys/libgcrypt` | `https://dev.gnupg.org/source/libgcrypt.git` | Crypto library for GnuPG-adjacent tools such as duplicity workflows. |

## P2 / 可选清单

| Local path | Upstream | Why it can wait |
|---|---|---|
| `sources/distributed-filesystems-security/ceph` | `https://github.com/ceph/ceph.git` | Huge distributed storage system with CephFS auth, snapshots, checksums, and object storage. Valuable but can dominate line count and attention. |
| `sources/distributed-filesystems-security/glusterfs` | `https://github.com/gluster/glusterfs.git` | Distributed filesystem with translator stack, replication, geo-replication, and ACL/xattr behavior. Include for historical distributed FS study. |
| `sources/distributed-filesystems-security/juicefs` | `https://github.com/juicedata/juicefs.git` | Object-store-backed POSIX filesystem with metadata engine, caching, compression, and encryption options. |
| `sources/distributed-filesystems-security/seaweedfs` | `https://github.com/seaweedfs/seaweedfs.git` | Distributed object/file store with Filer semantics and replication; useful if distributed tree metadata is in scope. |
| `sources/distributed-filesystems-security/ipfs-kubo` | `https://github.com/ipfs/kubo.git` | Content-addressed distributed data system. Not POSIX-first, but useful for Merkle DAG comparison. |
| `sources/kernel-core/blktests` | `https://github.com/osandov/blktests.git` | Block-layer tests; include when studying dm-crypt/LUKS boundary behavior. |
| `sources/tests-fuzzing/fio` | `https://github.com/axboe/fio.git` | IO workload generator for reproducing filesystem behavior. Not itself a filesystem source. |
| `sources/tests-fuzzing/syzbot-syzkaller` | `https://github.com/google/syzkaller.git` | Kernel filesystem fuzzing context. Include when test/fuzz slice is ready. |
| `sources/backup-dedup-encrypted/rustic` | `https://github.com/rustic-rs/rustic.git` | Restic-compatible Rust implementation. Useful for format comparison if Restic internals are being studied deeply. |
| `sources/backup-dedup-encrypted/zbackup` | `https://github.com/zbackup/zbackup.git` | Historical deduplicating backup design. Include only for lineage. |

## Explicit Exclusions / 不收

| Project family | Decision | Reason |
|---|---|---|
| Time Machine, iCloud Drive, OneDrive, Dropbox, Google Drive desktop clients | Exclude | Not source-first, often proprietary, and not useful for source-only repository goals. |
| Veeam, Acronis, Backblaze client, CrashPlan, Arq, Carbon Copy Cloner | Exclude | Mostly proprietary or product-centric. They may be operationally important, but not suitable source targets. |
| rsnapshot, deja-dup, Timeshift | Usually exclude | Mostly orchestration around rsync, duplicity, or btrfs snapshots. Include only if a later UX/policy slice needs wrappers. |
| tar, cpio, pax | Exclude from Agent 09 P0 | Important archive formats but too generic; can be collected by base Unix/tooling Agents. |
| Kubernetes/CSI backup operators | Exclude | Cluster orchestration, not local/distributed file-tree source semantics. |
| Cloud SDKs and object-store clients | Exclude by default | Include only specific libraries required by Borg/Restic/Kopia/Rclone build or backend behavior. |
| Distro package recipes | Exclude from source core | Track only when patches alter encryption, integrity, metadata, or sync behavior. |

## Suggested Study Order

1. Read Linux VFS/security primitives first: path lookup, inode permissions,
   xattrs, ACLs, capabilities, keyrings, `fs/crypto`, `fs/verity`, `fs/ecryptfs`,
   btrfs, EROFS, SquashFS, overlayfs.
2. Pair kernel features with userspace: `fscrypt`, `fsverity-utils`,
   `keyutils`, `acl`, `attr`, `libcap`, `cryptsetup`.
3. Compare encrypted file-tree approaches: native fscrypt, eCryptfs stacked
   filesystem, EncFS/gocryptfs file-per-file overlays, CryFS block abstraction,
   and LUKS/dm-crypt as the block-layer contrast.
4. Compare backup repository designs: Borg, Restic, Kopia, then Attic/bup/
   Duplicity/Duplicacy only if lineage or alternative formats matter.
5. Compare synchronization designs: rsync delta transfer, Syncthing block
   exchange and conflict/versioning, Unison reconciliation, git-annex location
   tracking.
6. Compare versioned tree deployment: Git object model, git-annex, OSTree,
   casync, composefs, SquashFS/EROFS images, btrfs/ZFS send/receive.
7. Add distributed filesystems only after the above is stable, because Ceph and
   Gluster can consume the line-count and review budget.

## Expected Size Control

This Agent 09 slice can fit the requested 20M-200M source-line envelope:

- Minimum useful set: Linux + fscrypt/fsverity tools + FUSE encrypted filesystems
  + Borg/Restic/Kopia + Syncthing/rsync/git-annex + OSTree/casync + btrfs/ZFS
  userspace + ACL/xattr/cap/keyutils. This should exceed the lower bound mainly
  because Linux and OpenZFS are large.
- Avoid adding Ceph, GlusterFS, IPFS, full crypto libraries, and every historical
  backup tool at the same time unless the combined repository needs more breadth.
- Use shallow clones for first import, then deepen individual repositories when
  studying history-sensitive security fixes or on-disk/repository format changes.

## Omission Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Missing kernel-side implementation while collecting only tools | `fscrypt`, `fsverity`, eCryptfs, btrfs, EROFS, SquashFS, ACLs, capabilities, keyrings, and IMA/EVM all depend on kernel behavior. | Linux must be P0, not optional. Keep notes mapping each userspace tool to kernel directories. |
| Treating backup programs as generic utilities | Many backup tools do not implement interesting tree semantics; others implement critical chunking/encryption metadata. | Keep Borg/Restic/Kopia P0; require a file-tree semantics reason for every additional backup tool. |
| Forgetting metadata fidelity | Security semantics often live in xattrs, ACLs, caps, SELinux labels, hard links, sparse files, mtimes, device nodes, and symlinks. | Include `acl`, `attr`, `libcap`, SELinux/IMA tools, and tests that exercise metadata. |
| Overweighting cloud sync clients | GUI sync clients can add code without teaching core algorithms. | Prefer Syncthing, rsync, Unison, csync, git-annex; avoid proprietary clients and GUI-heavy wrappers. |
| Missing stale/security-broken lineage | EncFS and eCryptfs are historically important but not modern best practice. | Keep them as comparative/historical sources with explicit warnings. |
| Confusing block encryption with filesystem encryption | LUKS/dm-crypt protects blocks but not file-tree semantics. | Keep `cryptsetup` as boundary comparison, not as a replacement for fscrypt/eCryptfs/FUSE encryption. |
| Ignoring repository/on-disk format migration code | Backup and versioned-tree security often fails at upgrade, prune, repair, or compaction paths. | Read maintenance code: Borg compact/check, Restic prune/check, Kopia maintenance, OSTree fsck/static deltas, git-annex repair/fsck. |
| Losing canonical source due to hosting quirks | eCryptfs userspace is Launchpad/Bazaar; git-annex canonical source uses `git://`; some GitHub repos hit API limits. | Record canonical URL plus mirror fallback only after verification. Use `git ls-remote` or project pages for validation. |
| Missing license or generated-vendored source boundaries | Some large Go/Rust projects vendor dependencies or generate code. | Track vendored code separately in inventory; do not count generated/vendor trees as primary design code unless required for reproducible builds. |

## Verification Checklist

Run these checks before the slice is accepted into the combined `learn_fs`
repository:

```bash
# 1. Verify source URLs resolve.
while read -r url; do
  git ls-remote --heads "$url" >/dev/null || echo "FAILED $url"
done < Docs/agent09-url-list.txt

# 2. Confirm Linux kernel directories relevant to this slice exist.
test -d sources/kernel-core/linux/fs/crypto
test -d sources/kernel-core/linux/fs/verity
test -d sources/kernel-core/linux/fs/ecryptfs
test -d sources/kernel-core/linux/security/integrity

# 3. Confirm userspace tools have expected entry points.
test -e sources/kernel-core/fscrypt
test -e sources/kernel-core/fsverity-utils
test -e sources/backup-dedup-encrypted/borg
test -e sources/backup-dedup-encrypted/restic
test -e sources/backup-dedup-encrypted/kopia
test -e sources/sync-replication/syncthing
test -e sources/sync-replication/rsync
test -e sources/content-addressed-versioned/git-annex
test -e sources/content-addressed-versioned/ostree
test -e sources/content-addressed-versioned/casync

# 4. Measure size without generated build outputs.
cloc sources \
  --exclude-dir=.git,node_modules,vendor,target,build,dist,out,__pycache__ \
  --timeout 0
```

Create `Docs/agent09-url-list.txt` from the upstream column after the final
combined list is approved. Bazaar-only sources such as Launchpad eCryptfs need a
separate `bzr info`/`brz info` validation path rather than `git ls-remote`.

For the P0 Git-only set, the initial `Docs/agent09-url-list.txt` can start with:

```text
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
https://github.com/google/fscrypt.git
https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git
https://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git
https://github.com/libfuse/libfuse.git
https://github.com/rfjakob/gocryptfs.git
https://github.com/cryfs/cryfs.git
https://github.com/vgough/encfs.git
https://github.com/borgbackup/borg.git
https://github.com/restic/restic.git
https://github.com/kopia/kopia.git
https://github.com/syncthing/syncthing.git
https://git.samba.org/rsync.git
git://git-annex.branchable.com/
https://github.com/ostreedev/ostree.git
https://github.com/systemd/casync.git
https://git.kernel.org/pub/scm/linux/kernel/git/kdave/btrfs-progs.git
https://github.com/openzfs/zfs.git
https://github.com/plougher/squashfs-tools.git
https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git
https://git.savannah.nongnu.org/git/acl.git
https://git.savannah.nongnu.org/git/attr.git
https://git.kernel.org/pub/scm/libs/libcap/libcap.git
https://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git
https://gitlab.com/cryptsetup/cryptsetup.git
```

## Upstream URL Validation Notes

The following upstreams were directly probed during this Agent 09 pass:

- Linux: `https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git`
- fsverity-utils: `https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git`
- libfuse: `https://github.com/libfuse/libfuse.git`
- ACL: `https://git.savannah.nongnu.org/git/acl.git`
- attr: `https://git.savannah.nongnu.org/git/attr.git`
- keyutils: `https://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git`
- libcap: `https://git.kernel.org/pub/scm/libs/libcap/libcap.git`
- btrfs-progs: `https://git.kernel.org/pub/scm/linux/kernel/git/kdave/btrfs-progs.git`
- erofs-utils: `https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git`
- squashfs-tools: `https://github.com/plougher/squashfs-tools.git`
- OpenZFS: `https://github.com/openzfs/zfs.git`
- rsync: `https://git.samba.org/rsync.git`
- git-annex canonical source: `git://git-annex.branchable.com/`
- casync: `https://github.com/systemd/casync.git`
- OSTree: `https://github.com/ostreedev/ostree.git`
- eCryptfs project page: `https://launchpad.net/ecryptfs`; Launchpad lists
  userspace source at `https://code.launchpad.net/~ecryptfs/ecryptfs/trunk`.

GitHub API access was rate-limited in this environment, but normal HTTPS page
access worked for several GitHub projects. Re-run URL validation from the final
import machine before creating submodules.

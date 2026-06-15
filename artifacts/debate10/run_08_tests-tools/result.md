# Agent 08: File-System Test, Validation, Benchmark, Fault-Injection, and Format-Tool Sources

Generated on 2026-06-15 for the `learn_fs` source-only research repository.

## Boundary

Agent 08 covers source code used to test, validate, stress, benchmark, corrupt, repair, encrypt, verify, mount, image, and format file systems. It intentionally does not replace the main file-system implementation agents. The goal is to make `learn_fs` useful for reading how file systems are exercised and diagnosed, not only how they are implemented.

Source-only means:

- Include upstream Git repositories, build/test scripts, harnesses, and checked-in test cases.
- Exclude generated disk images, test run output, VM snapshots, corpora produced by fuzzers, benchmark result archives, coverage databases, and package-manager caches.
- Keep binary fixtures only when they are small, upstream checked-in test inputs and necessary to understand the source tests.
- Prefer authoritative upstreams over distribution mirrors.

This slice alone is not expected to carry the full 20M-200M line target unless optional distributed-system and virtualization tooling is included. It is designed to compose with kernel, FUSE, distributed FS, and userspace FS implementation slices.

## Recommended Layout

```text
learn_fs/
  Docs/
    agent08_testing_validation_tools.md
    agent08_source_fetch_manifest.tsv
  sources/
    40_tests/
      fstests/
        xfstests-dev/
        xfstests-bld/
      block/
        blktests/
      syscall_posix/
        ltp/
        pjdfstest/
      stress/
        fsstress_from_fstests/
        fsx_from_fstests/
        syzkaller/
      distributed_protocol/
        pynfs/
        cthon04/
        samba/
        unionmount-testsuite/
    41_benchmarks/
      fio/
      filebench/
      fs_mark/
      ior/
      iozone/                 # optional, confirm source/license before mirroring
      dbench_or_samba_torture/ # optional, usually covered by samba/
    42_fault_injection/
      crashmonkey/
      kdevops/
      qemu/
      nbd/
      liburing/
      device_mapper_tools_from_lvm2_or_cryptsetup/
    43_format_repair_tools/
      ext/
        e2fsprogs/
      xfs/
        xfsprogs-dev/
        xfsdump-dev/
      btrfs/
        btrfs-progs/
      f2fs/
        f2fs-tools/
      fat_exfat/
        dosfstools/
        exfatprogs/
      ntfs/
        ntfs-3g/
      erofs/
        erofs-utils/
      squashfs/
        squashfs-tools/
      ubifs_jffs2/
        mtd-utils/
      udf/
        udftools/
      zfs/
        zfs/
      bcachefs/
        bcachefs-tools/
      partitions/
        util-linux/
        parted/
    44_security_integrity/
      fsverity-utils/
      fscrypt/
      cryptsetup/
    45_mount_protocol_tools/
      nfs-utils/
      cifs-utils/
      libfuse/
      sshfs/
      s3fs-fuse/
    46_image_vm_tools/
      libguestfs/
      guestfs-tools/
      qemu/
      nbd/
      libblockdev/
      nvme-cli/
    49_observability_coverage/
      strace/
      lcov/
```

Directory numbers deliberately place this slice after primary implementation sources. The layout keeps source family and study purpose visible without pretending these projects share one build system.

## MUST Collect

These are high-signal, source-first repositories for file-system testing and file-system tool behavior. They should be mirrored before broad optional material.

| Area | Repository | Upstream | Why it is mandatory |
|---|---|---|---|
| Generic FS regression | `xfstests-dev` | https://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git | Primary Linux file-system regression suite despite the historical XFS name; includes generic, ext4, XFS, btrfs, overlay, NFS, tmpfs and stress tests. Also contains canonical `fsstress` and `fsx` sources. |
| fstests automation | `xfstests-bld` | https://github.com/tytso/xfstests-bld.git | Builds and runs fstests in reproducible VM/test-appliance flows; useful for studying operationalization of fstests. |
| Block-layer validation | `blktests` | https://github.com/osandov/blktests.git | Regression tests for block stack behavior that file systems depend on: NVMe, SCSI, loop, dm, md, nbd, zbd, and io_uring paths. |
| Linux syscall/LTP coverage | `ltp` | https://github.com/linux-test-project/ltp.git | Broad Linux kernel/userspace test suite with file-system, VFS, syscalls, quota, fsnotify, AIO, mmap, tmpfs, mount, and network-FS coverage. |
| POSIX FS semantics | `pjdfstest` | https://github.com/pjd/pjdfstest.git | Compact POSIX file-system semantic tests; useful for comparing local FS, FUSE FS, network FS, and non-Linux semantics. |
| Benchmark engine | `fio` | https://github.com/axboe/fio.git | De facto flexible I/O workload generator; source is essential for understanding workload semantics, engines, verification, latency accounting, and replay. |
| ext tooling | `e2fsprogs` | https://git.kernel.org/pub/scm/fs/ext2/e2fsprogs.git | `mke2fs`, `e2fsck`, `debugfs`, libext2fs, ext2/3/4 repair and image tooling. |
| XFS tooling | `xfsprogs-dev` | https://git.kernel.org/pub/scm/fs/xfs/xfsprogs-dev.git | `mkfs.xfs`, `xfs_repair`, `xfs_db`, `xfs_io`, quota/admin tooling and libraries. |
| FAT tooling | `dosfstools` | https://github.com/dosfstools/dosfstools.git | `mkfs.fat`, `fsck.fat`; small but important for boot/media/file-format study. |
| exFAT tooling | `exfatprogs` | https://github.com/exfatprogs/exfatprogs.git | Linux exFAT `mkfs`, `fsck`, `dump`, `label`, `tune` tools. |
| F2FS tooling | `f2fs-tools` | https://git.kernel.org/pub/scm/linux/kernel/git/jaegeuk/f2fs-tools.git | Flash-friendly FS creation, repair, dump, resize, compression and zoned-media tooling. |
| NTFS tooling | `ntfs-3g` | https://github.com/tuxera/ntfs-3g.git | NTFS userspace driver and `mkntfs`, `ntfsfix`, `ntfsclone`, `ntfsresize`, metadata tools. |
| Btrfs tooling | `btrfs-progs` | https://github.com/kdave/btrfs-progs.git | `mkfs.btrfs`, `btrfs check`, send/receive, inspect-internal, rescue, balance, scrub tooling. |
| fs-verity | `fsverity-utils` | https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git | Userspace tooling for Linux fs-verity metadata generation, signing and verification workflows. |
| fscrypt | `fscrypt` | https://github.com/google/fscrypt.git | Userspace management tool for Linux native file-system encryption policies. |

## SHOULD Collect

These fill important coverage gaps and are still close to Agent 08's scope. Include them unless storage or time is constrained.

| Area | Repository | Upstream | Why collect |
|---|---|---|---|
| Crash consistency | `crashmonkey` | https://github.com/utsaslab/crashmonkey.git | Research-grade crash-consistency testing and workload checking for file systems. |
| Kernel fuzzing | `syzkaller` | https://github.com/google/syzkaller.git | Fuzzing infrastructure with many VFS/file-system reproducer paths and syscall descriptions. Store source only, not generated corpora. |
| FS benchmark | `filebench` | https://github.com/filebench/filebench.git | Workload model language and classic file-server/database/mail/webserver profiles. |
| Metadata benchmark | `fs_mark` | https://github.com/josefbacik/fs_mark.git | Small-file and metadata create/delete workload benchmark. |
| HPC I/O benchmark | `ior` | https://github.com/hpc/ior.git | Distributed/HPC I/O benchmark, useful for parallel FS and object/storage-backed FS study. |
| Overlay/union semantics | `unionmount-testsuite` | https://github.com/amir73il/unionmount-testsuite.git | Tests overlay/union mount behavior and whiteout/copy-up semantics. |
| NFS tooling | `nfs-utils` | https://github.com/linux-nfs/nfs-utils.git | Linux NFS client/server userspace utilities and mount tooling. |
| NFS protocol tests | `pynfs` | https://github.com/linux-nfs/pynfs.git | NFSv4 protocol test suite. |
| Legacy NFS tests | `cthon04` | https://github.com/phdeniel/cthon04.git | Historic but still useful NFS interoperability tests. |
| SMB/CIFS stack tests | `samba` | https://github.com/samba-team/samba.git | Includes `smbtorture`, VFS modules, protocol and file-semantics test infrastructure. |
| CIFS mount tools | `cifs-utils` | https://git.samba.org/cifs-utils.git | Linux CIFS mount helper and admin utilities. |
| FUSE library | `libfuse` | https://github.com/libfuse/libfuse.git | Core userspace file-system interface library and examples/tests. |
| SSHFS | `sshfs` | https://github.com/libfuse/sshfs.git | Representative FUSE network file-system client. |
| Object-store FUSE | `s3fs-fuse` | https://github.com/s3fs-fuse/s3fs-fuse.git | Representative FUSE/object-storage adapter. |
| VM/test orchestration | `kdevops` | https://github.com/linux-kdevops/kdevops.git | Kernel and file-system test automation used around fstests and storage validation. |
| Emulation | `qemu` | https://gitlab.com/qemu-project/qemu.git | VM/block-device emulation and fault/test platform source. Include once globally if another agent already owns it. |
| Network block device | `nbd` | https://github.com/NetworkBlockDevice/nbd.git | NBD server/client tooling used in image and failure-path experiments. |
| io_uring support | `liburing` | https://github.com/axboe/liburing.git | Library and tests for Linux io_uring, increasingly relevant to FS and block benchmarks. |
| Guest image tooling | `libguestfs` | https://github.com/libguestfs/libguestfs.git | Source for inspecting and modifying disk images through appliance workflows. |
| Guest image tools | `guestfs-tools` | https://github.com/libguestfs/guestfs-tools.git | Higher-level VM/image utilities around libguestfs. |
| Block-device library | `libblockdev` | https://github.com/storaged-project/libblockdev.git | Block-device operation library used by storage management stacks. |
| NVMe tooling | `nvme-cli` | https://github.com/linux-nvme/nvme-cli.git | NVMe admin/testing commands and source-level insight for storage device behavior. |
| Tracing | `strace` | https://github.com/strace/strace.git | Essential for studying syscall-level FS behavior and tests. |
| Coverage | `lcov` | https://github.com/linux-test-project/lcov.git | Coverage tooling for test evaluation; source only. |

## Format and Repair Tool Extensions

These are not all mandatory, but they materially improve coverage of disk formats, read-only/compressed formats, flash formats, and modern Linux file systems.

| Priority | Repository | Upstream | Notes |
|---|---|---|---|
| SHOULD | `erofs-utils` | https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git | `mkfs.erofs`, fsck, dump, image tools for EROFS. |
| SHOULD | `squashfs-tools` | https://github.com/plougher/squashfs-tools.git | `mksquashfs`, `unsquashfs`; important for compressed read-only images. |
| SHOULD | `mtd-utils` | https://git.kernel.org/pub/scm/linux/kernel/git/rw/mtd-utils.git | UBI/UBIFS/JFFS2 flash tools. |
| SHOULD | `util-linux` | https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git | `mount`, `umount`, `findmnt`, `lsblk`, `blkid`, `wipefs`, `losetup`, `fsck`, `mkfs` wrappers. |
| SHOULD | `parted` | https://git.savannah.gnu.org/git/parted.git | Partition-table and disk-label manipulation source. |
| SHOULD | `xfsdump-dev` | https://git.kernel.org/pub/scm/fs/xfs/xfsdump-dev.git | XFS dump/restore tooling. |
| SHOULD | `cryptsetup` | https://gitlab.com/cryptsetup/cryptsetup.git | LUKS/dm-crypt userspace source, relevant to encrypted FS test stacks. |
| OPTIONAL | `openzfs/zfs` | https://github.com/openzfs/zfs.git | Large implementation plus tests and `zpool`/`zfs` tools; collect if ZFS is in global scope. |
| OPTIONAL | `bcachefs-tools` | https://github.com/koverstreet/bcachefs-tools.git | Userspace tools for bcachefs. |
| OPTIONAL | `udftools` | https://github.com/pali/udftools.git | UDF format tools. |
| OPTIONAL | `nilfs-utils` | https://github.com/nilfs-dev/nilfs-utils.git | NILFS userspace utilities. |
| OPTIONAL | `mtools` | https://www.gnu.org/software/mtools/ | Useful FAT userspace tools, but confirm authoritative Git source before mirroring. |
| OPTIONAL | JFS/ReiserFS utilities | distro or archival upstreams | Historical value only; previous common GitHub mirrors did not validate cleanly. Do not make them core. |

## Distributed and Parallel File-System Validation

Agent 08 should collect tests and harnesses for distributed behavior, but avoid pulling every distributed FS implementation merely to get tests unless another agent also needs the implementation.

| Priority | Repository | Upstream | Notes |
|---|---|---|---|
| SHOULD | `samba` | https://github.com/samba-team/samba.git | Best public source for SMB protocol testing and `smbtorture`. Large but worthwhile. |
| SHOULD | `pynfs` | https://github.com/linux-nfs/pynfs.git | NFSv4 protocol tests. |
| SHOULD | `cthon04` | https://github.com/phdeniel/cthon04.git | NFS interoperability tests. |
| SHOULD | `nfs-utils` | https://github.com/linux-nfs/nfs-utils.git | Linux NFS mount/server userspace source. |
| OPTIONAL | `ceph` | https://github.com/ceph/ceph.git | Huge distributed storage system with CephFS tests/tools. Include if global line budget needs a major distributed FS implementation and tests. |
| OPTIONAL | `teuthology` | https://github.com/ceph/teuthology.git | Ceph test orchestration source. Include with Ceph. |
| OPTIONAL | `glusterfs` | https://github.com/gluster/glusterfs.git | Distributed FS implementation and tests; include if global distributed FS scope includes Gluster. |
| OPTIONAL | `lustre-release` | https://github.com/lustre/lustre-release.git | HPC distributed FS implementation and tests; include if global scope includes Lustre. |

## Exclude or Quarantine

Do not mirror these into the source tree as normal source repositories:

- Generated fstests result directories: `results/`, `check.time`, `*.full`, `*.out.bad`, VM console logs.
- Fuzzer outputs: syzkaller workdirs, crash corpora, minimized reproducers generated locally unless a small selected sample is documented separately.
- Benchmark outputs: fio JSON results, blktrace captures, flamegraphs, perf data, latency histograms.
- Disk images: qcow2/raw/vmdk/vhdx, loopback images, VM snapshots, seed images, installer ISOs, cloud images.
- Large binary corpora and package caches.
- Distribution package source mirrors when an authoritative upstream Git exists.
- Proprietary storage vendor test suites, private conformance suites, and closed NAS/SAN tools.
- Checked-out build trees that vendor generated dependencies or download caches under the source directory.

If a project has upstream checked-in binary fixtures, keep them only if they are small and necessary for tests; otherwise record the upstream tag and omit the fixture from a source-only mirror.

## Line-Count Budget Guidance

Approximate source-size tiers for planning:

- Minimal Agent 08 core: `xfstests`, `xfstests-bld`, `blktests`, `ltp`, `pjdfstest`, `fio`, and core mkfs/fsck tools. Expect a compact but high-value set, likely under the global 20M-line floor by itself.
- Full test/tool slice: add benchmark, crash/fuzz, protocol tests, FUSE clients, image/VM/block utilities, observability and all format tools. This is a strong mid-size support slice.
- Distributed expansion: add Samba, Ceph, GlusterFS, Lustre, QEMU, and possibly OpenZFS. This can move the whole `learn_fs` repository toward tens of millions of lines and should be coordinated with other agents to avoid duplicate ownership.

The 200M-line ceiling is mainly at risk if every large distributed storage project, all VM infrastructure, and broad dependency closures are mirrored with history and generated artifacts. Prefer shallow or blobless mirrors for initial review, then pin exact commits.

## Validation

Run these checks before accepting Agent 08 sources into `learn_fs`.

### 1. Upstream Reachability

For every row in `Docs/agent08_source_fetch_manifest.tsv` with status `MUST` or `SHOULD`:

```bash
awk -F '\t' 'NR > 1 && ($1 == "MUST" || $1 == "SHOULD") {print $5}' \
  Docs/agent08_source_fetch_manifest.tsv |
while read -r url; do
  git ls-remote --symref "$url" HEAD >/dev/null || echo "FAIL $url"
done
```

On 2026-06-15, the mandatory and recommended upstreams in this document were spot-checked with `git ls-remote --symref HEAD`. The default branch names and HEAD commit prefixes are captured in the TSV where available.

### 2. Source-Only Gate

After cloning sources under `sources/`, reject obvious generated assets:

```bash
find sources -type f \( \
  -name '*.qcow2' -o -name '*.raw' -o -name '*.vmdk' -o -name '*.vhdx' -o \
  -name '*.iso' -o -name '*.img' -o -name '*.trace' -o -name '*.pcap' -o \
  -name '*.perf.data' -o -name '*.gcda' -o -name '*.gcno' \) -print
```

Some upstream projects legitimately contain tiny `.img` or binary fixtures. Keep exceptions in a reviewed allowlist, not by default.

### 3. Duplicate Ownership Gate

Large projects should have one owner in the global `learn_fs` plan:

- `qemu`: Agent 08 needs it for test/fault platforms; another virtualization agent may own it.
- `samba`: Agent 08 needs SMB tests; a distributed/protocol agent may own implementation study.
- `ceph`, `glusterfs`, `lustre-release`, `openzfs`: collect only if global scope includes those implementations or their test harnesses are explicitly needed.
- `linux`: Agent 08 references in-tree tests and tools, but the kernel source itself should be owned by the core kernel/FS implementation slice.

### 4. Functional Smoke Tests

Use build-system-specific smoke checks without running destructive tests on the host:

```bash
make -C sources/40_tests/fstests/xfstests-dev help || true
make -C sources/41_benchmarks/fio --dry-run || true
make -C sources/43_format_repair_tools/ext/e2fsprogs --dry-run || true
make -C sources/43_format_repair_tools/xfs/xfsprogs-dev --dry-run || true
```

Do not run fstests, fsck repair tests, crash tests, fio write workloads, or mkfs commands against host disks. Use disposable loop devices or VMs only.

### 5. Coverage Checklist

Accept the slice only if all of these coverage groups have at least one source repository:

- General file-system regression: `xfstests-dev`.
- Block layer validation: `blktests`.
- POSIX/syscall semantics: `ltp` and `pjdfstest`.
- Stress and randomized workloads: `fsstress`, `fsx`, `fio`, optionally `syzkaller`.
- Benchmarks: `fio`, plus at least one of `filebench`, `fs_mark`, `ior`.
- Format/repair: ext, XFS, FAT/exFAT, F2FS, NTFS, Btrfs.
- Integrity/encryption: `fsverity-utils`, `fscrypt`, optionally `cryptsetup`.
- Network/distributed protocol: NFS and SMB/CIFS test/tool sources.
- Image/block/VM tooling: at least one of `qemu`, `nbd`, `libguestfs`, `libblockdev`.

## Omission Risks

- Relying only on fstests misses POSIX edge cases that `pjdfstest` captures, and misses broad syscall regression coverage in LTP.
- Relying only on fio misses file-system semantic failures; fio is a workload generator, not a correctness oracle.
- Omitting `blktests` hides failures in block-layer primitives that surface as file-system failures.
- Omitting mkfs/fsck tool sources makes on-disk format study one-sided: the kernel reader/writer is only half of the format contract.
- Omitting network protocol tests leaves NFS/SMB/parallel FS behavior underrepresented, especially locking, rename, delegation, lease, cache coherency, and reconnect semantics.
- Omitting crash/fault tools weakens study of journaling, ordering, fsync, replay, repair, and corruption behavior.
- Including generated images and benchmark results will distort source line counts, waste storage, and make updates unreproducible.
- Mirroring every large distributed storage implementation under Agent 08 can overrun the budget and duplicate other agents. Treat them as optional unless the global plan assigns ownership here.

## Practical Study Order

1. Read `xfstests-dev/common/`, `tests/generic/`, `ltp/testcases/kernel/fs/`, `pjdfstest/tests/`, and fio's verification/workload code.
2. Pair tests with tools: for ext/XFS/Btrfs/F2FS/NTFS/FAT, read mkfs, fsck/check, dump/debug, and repair code alongside related fstests.
3. Study crash and ordering behavior through `fsx`, `fsstress`, `CrashMonkey`, and selected syzkaller reproducers.
4. Study benchmark semantics in fio, filebench, fs_mark, and IOR before trusting any reported number.
5. Add NFS/SMB/FUSE protocol tests and mount tools to cover distributed and userspace FS behavior.
6. Only then add large distributed implementations or VM orchestration stacks if the global line budget and ownership map require them.

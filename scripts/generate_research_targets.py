#!/usr/bin/env python3
"""Generate language, level, OS-fit, and deduplication targets for learn_fs."""

from __future__ import annotations

import collections
import csv
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "manifests" / "sources.tsv"
TARGETS = ROOT / "manifests" / "research_targets.tsv"
DOCS = ROOT / "Docs"
OPTIMIZED_LOC = ROOT / "metrics" / "loc" / "optimized-focus" / "by-repo.csv"


FIELDS = [
    "source_id",
    "tier",
    "category",
    "path",
    "decision",
    "optimized_count",
    "priority",
    "study_stage",
    "fs_level",
    "fs_kind",
    "primary_languages",
    "language_priority",
    "os_fit",
    "covered_by",
    "rationale",
]


KEEP_NOW = {
    # OS and local Linux baseline.
    "linux",
    "freebsd-src",
    "openbsd-src",
    "netbsd-src",
    "dragonflybsd",
    "illumos-gate",
    "xnu",
    "reactos",
    "windows-driver-samples",
    "winfsp",
    "dokany",
    "winbtrfs",
    "e2fsprogs",
    "xfsprogs",
    "btrfs-progs",
    "f2fs-tools",
    "erofs-utils",
    "openzfs",
    "bcachefs",
    "bcachefs-tools",
    "util-linux",
    "lvm2",
    "cryptsetup",
    # User/network FS boundaries.
    "libfuse",
    "nfs-utils",
    "nfs-ganesha",
    "samba",
    "cifs-utils",
    "libnfs",
    # Distributed/parallel FS core.
    "ceph",
    "glusterfs",
    "lustre-release",
    "beegfs",
    "moosefs",
    "orangefs",
    "hadoop",
    "alluxio",
    "juicefs",
    "seaweedfs",
    "openafs",
    "coda",
    "xrootd",
    "eos",
    # Object-store adjacent systems that distributed FS stacks use as backends
    # or comparison points.
    "minio",
    "openstack-swift",
    "apache-ozone",
    "daos",
    "garage",
    "rustfs",
    # Tests and behavior gates.
    "xfstests",
    "blktests",
    "fio",
    "ltp",
    "pjdfstest",
    "ior",
    # Linux integrity/encryption primitives that change FS semantics.
    "fscrypt",
    "fsverity-utils",
}


SUPPORT_NEXT = {
    # Cross-OS comparison and mount frameworks.
    "freebsd-src",
    "openbsd-src",
    "netbsd-src",
    "dragonflybsd",
    "illumos-gate",
    "xnu",
    "reactos",
    "windows-driver-samples",
    "winfsp",
    "dokany",
    "winbtrfs",
    "macfuse",
    # Useful filesystem/tool coverage not needed in the first distributed pass.
    "dosfstools",
    "exfatprogs",
    "ntfs-3g",
    "udftools",
    "jfsutils",
    "squashfs-tools",
    "nilfs-utils",
    "bcache-tools",
    "mdadm",
    "parted",
    "thin-provisioning-tools",
    "vdo",
    "stratisd",
    "stratis-cli",
    "mtd-utils",
    "ocfs2-tools",
    "gfs2-utils",
    "dlm",
    # Cloud/image/virtualization and selected control plane.
    "fuse-overlayfs",
    "containers-storage",
    "containerd",
    "stargz-snapshotter",
    "nydus",
    "composefs",
    "qemu",
    "virtiofsd",
    "spdk",
    "nbd",
    "nbdkit",
    "libnbd",
    "rook",
    "ceph-csi",
    "beegfs-csi-driver",
    "juicefs-csi-driver",
    # More tests/security/sync.
    "xfstests-bld",
    "crashmonkey",
    "filebench",
    "fs-mark",
    "unionmount-testsuite",
    "pynfs",
    "cthon04",
    "kdevops",
    "liburing",
    "strace",
    "stress-ng",
    "iozone",
    "ecryptfs-utils",
    "gocryptfs",
    "cryfs",
    "encfs",
    "ima-evm-utils",
    "acl",
    "attr",
    "libcap",
    "keyutils",
    "selinux",
    "audit-userspace",
    "rsync",
    "syncthing",
    "restic",
    "borg",
    "kopia",
    "git-annex",
    "unison",
}


DEDUPED = {
    "linux-stable": "linux",
    "btrfs-linux": "linux+btrfs-progs",
    "kdave-linux": "linux+btrfs-progs",
    "linux-dm": "linux+lvm2",
    "kvdo": "linux+vdo",
    "ceph-client": "linux+ceph",
    "beegfs-rust": "beegfs",
    "beegfs-go": "beegfs",
    "beegfs-protobuf": "beegfs",
    "lizardfs": "moosefs",
    "minio-mc": "minio",
    "longhorn-engine": "longhorn",
    "fuse-overlayfs-snapshotter": "fuse-overlayfs+containerd",
    "nydus-snapshotter": "nydus+containerd",
    "composefs-rs": "composefs",
    "guestfs-tools": "libguestfs",
    "libtirpc": "nfs-utils",
    "rpcbind": "nfs-utils",
}


P0_IDS = {
    "linux",
    "e2fsprogs",
    "xfsprogs",
    "btrfs-progs",
    "openzfs",
    "libfuse",
    "nfs-utils",
    "nfs-ganesha",
    "samba",
    "ceph",
    "glusterfs",
    "lustre-release",
    "beegfs",
    "moosefs",
    "xfstests",
    "fio",
    "ltp",
}

P1_IDS = KEEP_NOW - P0_IDS


LANGUAGE_BY_ID = {
    "linux": "C",
    "linux-stable": "C",
    "freebsd-src": "C",
    "openbsd-src": "C",
    "netbsd-src": "C",
    "dragonflybsd": "C",
    "illumos-gate": "C",
    "plan9": "C",
    "9front": "C",
    "xnu": "C,C++",
    "reactos": "C,C++",
    "windows-driver-samples": "C,C++",
    "winfsp": "C",
    "dokany": "C,C++",
    "winbtrfs": "C",
    "xv6-riscv": "C",
    "xv6-public": "C",
    "minix": "C",
    "os161": "C",
    "pintos": "C",
    "e2fsprogs": "C",
    "xfsprogs": "C",
    "xfsdump": "C",
    "btrfs-progs": "C",
    "btrfs-linux": "C",
    "kdave-linux": "C",
    "f2fs-tools": "C",
    "erofs-utils": "C",
    "dosfstools": "C",
    "exfatprogs": "C",
    "ntfs-3g": "C",
    "udftools": "C",
    "jfsutils": "C",
    "reiserfsprogs": "C",
    "squashfs-tools": "C",
    "apfs-fuse": "C++",
    "linux-apfs-rw": "C",
    "openzfs": "C",
    "bcachefs": "C",
    "bcachefs-tools": "C",
    "nilfs-utils": "C",
    "nilfs2-kmod10": "C",
    "bcache-tools": "C",
    "util-linux": "C",
    "mdadm": "C",
    "parted": "C",
    "linux-dm": "C",
    "lvm2": "C",
    "thin-provisioning-tools": "C++",
    "cryptsetup": "C",
    "vdo": "C++",
    "kvdo": "C",
    "stratisd": "Rust",
    "stratis-cli": "Python",
    "devicemapper-rs": "Rust",
    "libcryptsetup-rs": "Rust",
    "libblkid-rs": "Rust",
    "libfuse": "C",
    "sshfs": "C",
    "go-fuse": "Go",
    "bazil-fuse": "Go",
    "pyfuse3": "Python,C",
    "fusepy": "Python",
    "s3fs-fuse": "C++",
    "gcsfuse": "Go",
    "blobfuse2": "Go",
    "mergerfs": "C++",
    "nfs-utils": "C",
    "nfs-ganesha": "C",
    "libnfs": "C",
    "go-nfs": "Go",
    "samba": "C,Python",
    "cifs-utils": "C",
    "ksmbd-tools": "C",
    "libsmb2": "C",
    "impacket": "Python",
    "smbj": "Java",
    "smblibrary": "C#",
    "davfs2": "C",
    "rclone": "Go",
    "ceph": "C++",
    "ceph-client": "C",
    "glusterfs": "C",
    "lustre-release": "C",
    "beegfs": "C,C++",
    "beegfs-rust": "Rust",
    "beegfs-go": "Go",
    "beegfs-protobuf": "Protocol Buffers",
    "moosefs": "C",
    "lizardfs": "C++",
    "orangefs": "C",
    "hadoop": "Java",
    "alluxio": "Java",
    "juicefs": "Go",
    "seaweedfs": "Go",
    "openafs": "C",
    "coda": "C,C++",
    "xrootd": "C++",
    "eos": "C++",
    "tahoe-lafs": "Python",
    "ipfs-kubo": "Go",
    "minio": "Go",
    "minio-mc": "Go",
    "openstack-swift": "Python",
    "apache-ozone": "Java",
    "daos": "C,C++",
    "garage": "Rust",
    "rustfs": "Rust",
    "rook": "Go",
    "longhorn": "Go",
    "ceph-csi": "Go",
    "beegfs-csi-driver": "Go",
    "juicefs-csi-driver": "Go",
    "csi-spec": "Protocol Buffers,Go",
    "mayastor": "Rust",
    "csi-driver-nfs": "Go",
    "csi-driver-smb": "Go",
    "csi-driver-iscsi": "Go",
    "longhorn-engine": "Go",
    "csi-driver-host-path": "Go",
    "external-snapshotter": "Go",
    "csi-lib-utils": "Go",
    "fuse-overlayfs": "C",
    "overlayfs-tools": "C",
    "fuse-overlayfs-snapshotter": "Go",
    "containers-storage": "Go",
    "containerd": "Go",
    "stargz-snapshotter": "Go",
    "nydus": "Rust",
    "nydus-snapshotter": "Go",
    "soci-snapshotter": "Go",
    "composefs": "C",
    "composefs-rs": "Rust",
    "moby": "Go",
    "buildkit": "Go",
    "cri-o": "Go",
    "overlaybd": "C++",
    "ostree": "C",
    "qemu": "C",
    "virtiofsd": "Rust",
    "spdk": "C",
    "nbd": "C",
    "nbdkit": "C",
    "libnbd": "C",
    "open-iscsi": "C",
    "libguestfs": "OCaml,C",
    "guestfs-tools": "C,OCaml",
    "libblockdev": "C",
    "nvme-cli": "C",
    "xfstests": "Shell,C",
    "xfstests-bld": "Shell,Python",
    "blktests": "Shell",
    "fio": "C",
    "ltp": "C,Shell",
    "pjdfstest": "Shell,C",
    "crashmonkey": "C++",
    "filebench": "C",
    "fs-mark": "C",
    "ior": "C",
    "unionmount-testsuite": "Shell",
    "pynfs": "Python",
    "cthon04": "C,Shell",
    "kdevops": "Ansible,Shell,Python",
    "liburing": "C",
    "mtd-utils": "C",
    "strace": "C",
    "lcov": "Perl",
    "stress-ng": "C",
    "iozone": "C",
    "fscrypt": "Go",
    "fsverity-utils": "C",
    "ecryptfs-utils": "C",
    "gocryptfs": "Go",
    "cryfs": "C++",
    "encfs": "C++",
    "ima-evm-utils": "C",
    "acl": "C",
    "attr": "C",
    "libcap": "C",
    "keyutils": "C",
    "selinux": "C",
    "audit-userspace": "C",
    "rsync": "C",
    "syncthing": "Go",
    "restic": "Go",
    "borg": "Python,C",
    "kopia": "Go",
    "git-annex": "Haskell",
    "casync": "C",
    "unison": "OCaml",
    "git-lfs": "Go",
    "git-crypt": "C++",
    "bup": "Python,C",
    "zstd": "C",
    "xz": "C",
    "lz4": "C",
    "zlib": "C",
    "syzkaller": "Go",
    "rocksdb": "C++",
    "leveldb": "C++",
    "pebble": "Go",
    "badger": "Go",
    "wiredtiger": "C",
    "sqlite": "C",
    "lmdb": "C",
    "foundationdb": "C++",
    "tikv": "Rust",
    "raft-engine": "Rust",
}


LEVEL_BY_CATEGORY = {
    "os-vfs": "L0 OS VFS/kernel",
    "windows-public": "L0/L1 public Windows FS stack",
    "teaching": "L0 teaching FS",
    "local-fs": "L1 local filesystem/tools",
    "cow-pools": "L1 local COW filesystem/pool",
    "block-storage": "L1 block/storage substrate",
    "user-network-fs": "L2 user/network filesystem",
    "distributed-fs": "L3 distributed/parallel filesystem",
    "object-store": "L4 object-store adjacent",
    "control-plane": "L5 orchestration/control-plane",
    "cloud-native": "L4 image/container filesystem layer",
    "virtualization": "L4 virtual/block filesystem substrate",
    "test-tools": "L6 validation/benchmark/fuzzing",
    "security-integrity": "L6 security/integrity semantics",
    "sync-backup": "L6 sync/backup/versioned tree",
    "compression": "L6 compression primitive",
    "storage-engines": "L6 storage-engine comparison",
}


FS_KIND_BY_CATEGORY = {
    "os-vfs": "os-fs",
    "windows-public": "os-fs",
    "teaching": "teaching",
    "local-fs": "local-fs",
    "cow-pools": "local-fs",
    "block-storage": "block-substrate",
    "user-network-fs": "network/user-fs",
    "distributed-fs": "distributed-fs",
    "object-store": "object-store-adjacent",
    "control-plane": "control-plane",
    "cloud-native": "image/container-fs",
    "virtualization": "virtual/block-substrate",
    "test-tools": "test-tool",
    "security-integrity": "security/integrity",
    "sync-backup": "sync/backup",
    "compression": "compression",
    "storage-engines": "storage-engine",
}


OS_FIT_BY_CATEGORY = {
    "os-vfs": "linux,macos,bsd",
    "windows-public": "windows",
    "teaching": "portable/teaching",
    "local-fs": "linux",
    "cow-pools": "linux,bsd",
    "block-storage": "linux",
    "user-network-fs": "linux,macos,windows-via-ports",
    "distributed-fs": "linux-first",
    "object-store": "linux,macos,windows-server/userspace",
    "control-plane": "linux/kubernetes",
    "cloud-native": "linux/container",
    "virtualization": "linux,macos,windows-host-via-ports",
    "test-tools": "linux-first",
    "security-integrity": "linux",
    "sync-backup": "linux,macos,windows",
    "compression": "portable",
    "storage-engines": "portable",
}


OS_FIT_BY_ID = {
    "linux": "linux",
    "linux-stable": "linux",
    "freebsd-src": "bsd",
    "openbsd-src": "bsd",
    "netbsd-src": "bsd",
    "dragonflybsd": "bsd",
    "illumos-gate": "illumos/solaris",
    "xnu": "macos/darwin",
    "macfuse": "macos",
    "reactos": "windows-compatible",
    "windows-driver-samples": "windows",
    "winfsp": "windows",
    "dokany": "windows",
    "winbtrfs": "windows",
    "ceph": "linux-first; clients on linux/macos/windows exist but CephFS kernel path is linux-first",
    "glusterfs": "linux-first",
    "lustre-release": "linux-first",
    "beegfs": "linux-first",
    "hadoop": "linux,macos,windows userspace",
    "alluxio": "linux,macos,windows userspace",
    "juicefs": "linux,macos,windows userspace/FUSE",
    "seaweedfs": "linux,macos,windows userspace/FUSE",
    "minio": "linux,macos,windows userspace",
    "openstack-swift": "linux-first",
    "apache-ozone": "linux,macos,windows userspace",
    "garage": "linux,macos,windows userspace",
    "rustfs": "linux,macos,windows userspace",
}


def load_sources() -> list[dict[str, str]]:
    with SOURCES.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def decision_for(repo_id: str) -> str:
    if repo_id in KEEP_NOW:
        return "keep"
    if repo_id in DEDUPED:
        return "dedup"
    if repo_id in SUPPORT_NEXT:
        return "support"
    return "defer"


def priority_for(repo_id: str, decision: str) -> str:
    if repo_id in P0_IDS:
        return "P0"
    if repo_id in P1_IDS:
        return "P1"
    if decision == "support":
        return "P2"
    if decision == "dedup":
        return "P3-dedup"
    return "P3"


def stage_for(row: dict[str, str], decision: str) -> str:
    category = row["category"]
    repo_id = row["id"]
    if decision == "dedup":
        return "deduplicated"
    if category in {"distributed-fs", "object-store"}:
        return "distributed-first"
    if category in {"os-vfs", "local-fs", "cow-pools", "block-storage", "user-network-fs"}:
        return "os-and-protocol-baseline"
    if category == "test-tools":
        return "validation"
    if repo_id in {"fscrypt", "fsverity-utils"}:
        return "semantics-support"
    if category in {"windows-public", "cloud-native", "virtualization", "control-plane"}:
        return "platform-support"
    return "later-comparison"


def language_priority(languages: str, row: dict[str, str]) -> str:
    category = row["category"]
    repo_id = row["id"]
    if repo_id in {"beegfs"}:
        return "C kernel/client paths first, then C++ daemons; Go/Rust management repos are secondary."
    if repo_id in {"ceph"}:
        return "C++ data path and metadata daemons first; Python/admin glue later."
    if repo_id in {"samba"}:
        return "C protocol/VFS modules first; Python tests/build glue later."
    if category in {"os-vfs", "local-fs", "cow-pools", "block-storage", "user-network-fs"}:
        if "C" in languages or "C++" in languages:
            return "C/C++ first because ABI, kernel, page-cache, repair, and protocol hot paths dominate."
    if category == "distributed-fs":
        if languages in {"Go", "Java", "Rust"}:
            return f"{languages} core is worth studying after C/C++ distributed FS; useful for userspace metadata/control tradeoffs."
        return "Study the C/C++ data path before tests, bindings, and management glue."
    if category == "object-store":
        if languages in {"Go", "Java", "Rust", "Python"}:
            return f"{languages} is acceptable for userspace distributed/object layers; compare after C/C++ FS data paths."
        return "Object-store substrate; study only where it explains distributed FS backend behavior."
    if category in {"control-plane", "cloud-native"} and "Go" in languages:
        return "Go control plane/snapshotter code is secondary to filesystem data-path source."
    if "Rust" in languages:
        return "Rust is useful for memory-safe userspace components; not the first stop for mature kernel FS internals."
    if "Go" in languages:
        return "Go is useful for distributed service/control-plane code; avoid treating it as kernel/hot-path FS baseline."
    return "Study only after the core FS path is understood."


def rationale(row: dict[str, str], decision: str, priority: str, covered_by: str) -> str:
    repo_id = row["id"]
    category = row["category"]
    if decision == "keep":
        if priority == "P0":
            return "First-pass source: core OS/protocol/distributed FS path or mandatory validation gate."
        return "Kept after dedupe as a distinct design family or backend needed for distributed-FS comparison."
    if decision == "support":
        return "Valid source but not first-pass count; use for OS/platform comparison, tooling, or operational integration."
    if decision == "dedup":
        return f"Covered by {covered_by}; keep as reference but do not count in the optimized first pass."
    if category == "storage-engines":
        return "Storage-engine internals are useful comparison material but not filesystem/distributed-filesystem source."
    if category == "compression":
        return "Primitive dependency; defer until a filesystem path requires implementation-level compression study."
    return "Legitimate source, deferred to keep the first pass focused and below the LOC ceiling."


def row_for(source: dict[str, str]) -> dict[str, str]:
    repo_id = source["id"]
    decision = decision_for(repo_id)
    priority = priority_for(repo_id, decision)
    languages = LANGUAGE_BY_ID.get(repo_id, "unknown")
    covered_by = DEDUPED.get(repo_id, "")
    return {
        "source_id": repo_id,
        "tier": source["tier"],
        "category": source["category"],
        "path": source["path"],
        "decision": decision,
        "optimized_count": "yes" if decision == "keep" else "no",
        "priority": priority,
        "study_stage": stage_for(source, decision),
        "fs_level": LEVEL_BY_CATEGORY.get(source["category"], "unknown"),
        "fs_kind": FS_KIND_BY_CATEGORY.get(source["category"], "unknown"),
        "primary_languages": languages,
        "language_priority": language_priority(languages, source),
        "os_fit": OS_FIT_BY_ID.get(repo_id, OS_FIT_BY_CATEGORY.get(source["category"], "unknown")),
        "covered_by": covered_by,
        "rationale": rationale(source, decision, priority, covered_by),
    }


def write_targets(rows: list[dict[str, str]]) -> None:
    with TARGETS.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_analysis(rows: list[dict[str, str]]) -> None:
    decision_counts = collections.Counter(row["decision"] for row in rows)
    keep_counts = collections.Counter(row["category"] for row in rows if row["optimized_count"] == "yes")
    language_counts = collections.Counter(row["primary_languages"] for row in rows if row["optimized_count"] == "yes")
    measured_lines = measured_repos = measured_missing = None
    if OPTIMIZED_LOC.exists():
        with OPTIMIZED_LOC.open(newline="") as handle:
            loc_rows = list(csv.DictReader(handle))
        measured_lines = sum(int(row["code_lines"]) for row in loc_rows)
        measured_repos = len(loc_rows)
        measured_missing = sum(1 for row in loc_rows if row["missing"] == "True")

    lines = [
        "# FS Language, Level, OS Fit, And Deduplication Analysis",
        "",
        "This document is generated from `manifests/sources.tsv` plus the",
        "first-pass deduplication policy in `scripts/generate_research_targets.py`.",
        "",
        "## Language Judgment",
        "",
        "For filesystem work, language priority depends on the layer.",
        "",
        "- `C`: still the first language for OS VFS, kernel filesystems, page cache,",
        "  block layer, syscall ABI, mount helpers, fsck/mkfs/repair tools, and",
        "  mature network protocols. It is the strongest baseline when the target",
        "  is large-scale, hot-path, OS-integrated filesystem behavior.",
        "- `C++`: strong for large userspace distributed filesystems and object/data",
        "  services where complex metadata, RPC, caching, placement, and recovery",
        "  logic dominate. Ceph, BeeGFS daemons, XRootD/EOS, RocksDB-style metadata",
        "  engines, and some storage substrates fit here.",
        "- `Rust`: good for new userspace filesystem components, image/snapshotter",
        "  tooling, safety-sensitive daemons, and storage services where ownership",
        "  clarity is valuable. It is not the first route for mature Linux kernel",
        "  filesystem internals, but it is not a detour for well-bounded userspace",
        "  components.",
        "- `Go`: weak fit for kernel/hot-path filesystem internals, but a strong fit",
        "  for distributed service code, metadata servers, object-store interfaces,",
        "  CSI/control-plane, sync/backup, and FUSE/object-backed filesystems when",
        "  network latency and operational complexity dominate CPU instruction cost.",
        "",
        "Practical rule: study C/C++ data paths first, then Rust/Go/Java systems as",
        "userspace distributed design alternatives. For mixed-language projects,",
        "read the data path before management glue.",
        "",
        "## Mixed-Language Priority",
        "",
        "| Project | Priority inside project | Reason |",
        "|---|---|---|",
        "| Ceph | C++ MDS/client/OSD/RADOS first; Python/admin later | Core distributed FS and object paths are C++. |",
        "| BeeGFS | C kernel client and C++ services first; Go/Rust management later | The filesystem behavior is in client/module/services. |",
        "| Samba | C SMB/VFS modules first; Python tests/build later | Protocol and VFS behavior are C. |",
        "| Lustre | C client/server/LNet first; scripts/tests later | Kernel/client/server hot paths are C. |",
        "| Hadoop/Alluxio/Ozone | Java core first; native bits later | The system model is JVM userspace, not OS kernel FS. |",
        "| JuiceFS/SeaweedFS/MinIO | Go core first, but after C/C++ FS baselines | Good distributed userspace systems; not kernel-level FS references. |",
        "| DAOS | C/C++ engine/VOS first; Python/tools later | The storage engine and distributed object paths are native. |",
        "| Nydus/composefs-rs/Mayastor/Garage/RustFS | Rust core first, but as userspace/container/object layer | Useful modern safety-oriented systems, secondary to OS FS internals. |",
        "",
        "## FS Level Marking",
        "",
        "- `L0 OS VFS/kernel`: Linux, BSDs, illumos, XNU, ReactOS/public Windows samples.",
        "- `L1 local filesystem/tools`: ext/XFS/Btrfs/F2FS/EROFS/ZFS/bcachefs and mkfs/fsck/repair tooling.",
        "- `L2 user/network filesystem`: FUSE, NFS, SMB/CIFS, WebDAV, object-backed mounts.",
        "- `L3 distributed/parallel filesystem`: CephFS, GlusterFS, Lustre, BeeGFS, MooseFS, OrangeFS, HDFS, Alluxio, JuiceFS, SeaweedFS, AFS/Coda, XRootD/EOS.",
        "- `L4 object/container/virtual substrate`: MinIO, Swift, Ozone, DAOS, Garage, RustFS, container snapshotters, QEMU/SPDK/NBD.",
        "- `L5 control plane`: CSI, Rook, Longhorn, Kubernetes storage glue.",
        "- `L6 validation/support`: xfstests, fio, LTP, fscrypt/fsverity, sync/backup, compression, storage engines.",
        "",
        "## OS Fit",
        "",
        "- Linux: primary target for kernel FS, local FS tools, NFS/SMB server paths,",
        "  and most distributed FS clients/servers.",
        "- macOS: realistic for userspace clients, FUSE/macFUSE, object-backed mounts,",
        "  Go/Java/Rust services, and XNU VFS comparison. It is not the main target",
        "  for Linux-first kernel/distributed FS internals.",
        "- Windows: realistic for WinFsp/Dokany/public driver samples, user-mode",
        "  clients, Go/Java/Rust services, and ReactOS comparison. Linux remains the",
        "  primary platform for most open distributed FS kernel clients.",
        "",
        "## Optimized First-Pass Result",
        "",
        f"- total source rows analyzed: {len(rows)}",
        f"- keep/count now: {decision_counts['keep']}",
        f"- support but do not count now: {decision_counts['support']}",
        f"- deduplicated against stronger source: {decision_counts['dedup']}",
        f"- deferred: {decision_counts['defer']}",
    ]
    if measured_lines is not None:
        lines.extend([
            f"- measured optimized focus-path checkouts: {measured_repos}",
            f"- missing optimized checkouts: {measured_missing}",
            f"- measured optimized code-like lines: {measured_lines}",
        ])

    lines.extend([
        "",
        "Kept rows by category:",
        "",
        "| Category | Count |",
        "|---|---:|",
    ])

    for category, count in sorted(keep_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend([
        "",
        "Kept rows by primary language label:",
        "",
        "| Primary language label | Count |",
        "|---|---:|",
    ])
    for language, count in sorted(language_counts.items()):
        lines.append(f"| {language} | {count} |")

    lines.extend([
        "",
        "The full row-level decision table is `manifests/research_targets.tsv`.",
        "",
    ])

    (DOCS / "fs-language-priority-analysis.md").write_text("\n".join(lines))


def write_optimized_doc(rows: list[dict[str, str]]) -> None:
    kept = [row for row in rows if row["optimized_count"] == "yes"]
    lines = [
        "# Optimized First-Pass Research Targets",
        "",
        "Generated from `manifests/research_targets.tsv`.",
        "",
        "This is the deduplicated first-pass set for studying distributed",
        "filesystems on top of OS/filesystem ground truth. It intentionally keeps",
        "C/C++ OS, protocol, and data-path source ahead of Rust/Go/Java systems,",
        "while retaining representative userspace distributed designs in Go, Java,",
        "Rust, and Python where they are materially different.",
        "",
        "| Priority | Source | Level | Kind | Languages | OS fit | Rationale |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in sorted(kept, key=lambda item: (item["priority"], item["category"], item["source_id"])):
        lines.append(
            "| {priority} | `{source_id}` | {fs_level} | {fs_kind} | {primary_languages} | {os_fit} | {rationale} |".format(**row)
        )

    lines.extend([
        "",
        "Rows marked `support`, `dedup`, and `defer` remain in",
        "`manifests/research_targets.tsv` so the exclusion rationale is auditable.",
        "",
    ])
    (DOCS / "optimized-research-targets.md").write_text("\n".join(lines))


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    rows = [row_for(source) for source in load_sources()]
    write_targets(rows)
    write_analysis(rows)
    write_optimized_doc(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate learn_fs repository docs from manifests/sources.tsv."""

from __future__ import annotations

import collections
import csv
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "manifests" / "sources.tsv"
DOCS = ROOT / "Docs"


def load_sources() -> list[dict[str, str]]:
    with SOURCES.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_target_repositories(rows: list[dict[str, str]]) -> None:
    by_category: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        by_category[row["category"]].append(row)

    lines: list[str] = [
        "# Target Source Repositories",
        "",
        "Generated from `manifests/sources.tsv`.",
        "",
        "This is the source-only target map for `learn_fs`. It is intentionally",
        "broader than a single reading pass: `required` is the default clone",
        "tier, `important` is part of the complete research boundary, and",
        "`adjacent` covers source that is valuable for design comparison but can",
        "be deferred when local disk or the 200M-line budget is tight.",
        "",
        "## Tier Rules",
        "",
        "- `required` - default source set for filesystem and distributed",
        "  filesystem study.",
        "- `important` - strong source additions needed for completeness or",
        "  cross-platform comparison.",
        "- `adjacent` - source that teaches nearby storage mechanisms, history,",
        "  or implementation tradeoffs, but should not displace core FS source.",
        "",
        "## Counting Rules",
        "",
        "The line-count gate is 20,000,000 to 200,000,000 code-like lines for",
        "checked-out source. Count source-like files from git-tracked trees;",
        "exclude VCS metadata, build outputs, release archives, binary images,",
        "firmware, VM/container images, package caches, generated artifacts, and",
        "vendored dependency dumps unless a dependency is explicitly listed as a",
        "source target here.",
        "",
        "Two metrics should be reported:",
        "",
        "- `focus-paths`: default. Count filesystem-relevant source paths listed",
        "  in `manifests/focus_paths.tsv`, after generated/vendor/build/doc",
        "  exclusions.",
        "- `full-repo`: secondary audit. Count source-like files across each",
        "  selected checkout after the same exclusions.",
        "",
        "Use `focus-paths` as the primary gate so large monorepos such as Linux,",
        "FreeBSD, QEMU, Hadoop, DAOS, Ceph, and containerd do not hide the",
        "filesystem signal behind unrelated source.",
        "",
        "## Repositories By Category",
        "",
    ]

    tier_order = {"required": 0, "important": 1, "adjacent": 2}
    for category in sorted(by_category):
        lines.extend([f"### {category}", "", "| Tier | ID | Local path | Upstream | Default count | Notes |", "|---|---|---|---|---|---|"])
        for row in sorted(by_category[category], key=lambda item: (tier_order.get(item["tier"], 9), item["id"])):
            lines.append(
                "| {tier} | `{id}` | `{path}` | {url} | {default_count} | {notes} |".format(**row)
            )
        lines.append("")

    (DOCS / "target-repositories.md").write_text("\n".join(lines).rstrip() + "\n")


def write_source_repositories(rows: list[dict[str, str]]) -> None:
    required_count = sum(1 for row in rows if row["tier"] == "required")
    important_count = sum(1 for row in rows if row["tier"] == "important")
    adjacent_count = sum(1 for row in rows if row["tier"] == "adjacent")
    default_count = sum(1 for row in rows if row["default_count"] == "yes")

    lines = [
        "# File System Source Repository List",
        "",
        "Generated from a 10-agent debate workflow on 2026-06-15.",
        "",
        "## Boundary",
        "",
        "`learn_fs` is a source-only corpus for local filesystems, OS VFS layers,",
        "network filesystems, distributed/parallel filesystems, object-store",
        "adjacent storage, container/virtualized storage, filesystem tools, tests,",
        "security/integrity/sync systems, and selected storage engines that",
        "directly teach filesystem mechanisms.",
        "",
        "It does not collect papers, blogs, docs sites, prebuilt packages, binary",
        "release payloads, VM images, container layers, benchmark datasets, closed",
        "product internals, leaked source, or proprietary-only systems.",
        "",
        "The manifest currently contains:",
        "",
        f"- `required`: {required_count} repositories",
        f"- `important`: {important_count} repositories",
        f"- `adjacent`: {adjacent_count} repositories",
        f"- default-counted for source LOC: {default_count} repositories",
        "",
        "## Authoritative Local Files",
        "",
        "- `manifests/sources.tsv` - canonical cloneable source list",
        "- `manifests/focus_paths.tsv` - must-check reading paths",
        "- `scripts/clone_sources.sh` - shallow partial clone driver",
        "- `scripts/lock_remotes.sh` - remote HEAD/ref lock report",
        "- `scripts/verify_sources.sh` - manifest and checkout verifier",
        "- `scripts/source_inventory.py` - source-like LOC counter",
        "",
        "## Complete Source Families",
        "",
        "The complete public-source boundary is represented by these families:",
        "",
        "- OS/VFS: Linux, FreeBSD, OpenBSD, NetBSD, DragonFly BSD, illumos, Plan 9/9front, ReactOS, public Windows FS frameworks/samples.",
        "- Local FS and tools: ext, XFS, Btrfs, F2FS, EROFS, ZFS, bcachefs, NILFS, bcache, FAT/exFAT, NTFS, UDF, JFS, SquashFS, APFS public readers, device-mapper/LVM/VDO/Stratis.",
        "- User/network FS: FUSE, SSHFS, NFS, NFS-Ganesha, SMB/Samba/CIFS/KSMBD, WebDAV, object-store mount layers.",
        "- Distributed FS: CephFS, GlusterFS, Lustre, BeeGFS, MooseFS/LizardFS, OrangeFS, HDFS, Alluxio, JuiceFS, SeaweedFS, OpenAFS, Coda, XRootD/EOS, Tahoe-LAFS, Kubo/IPFS as content-addressed contrast.",
        "- Object-store adjacent: MinIO, Swift, Ozone, DAOS, Garage, RustFS, relevant CSI/control-plane source.",
        "- Cloud/virtualized storage: fuse-overlayfs, containers/storage, containerd snapshotters, stargz, Nydus, SOCI, composefs, OSTree, QEMU block, virtiofsd, SPDK, NBD.",
        "- Testing/tools: xfstests, blktests, fio, LTP, pjdfstest, stress-ng/iozone and filesystem mkfs/fsck/repair tools.",
        "- Security/integrity/sync: fscrypt, fsverity, encrypted FUSE filesystems, IMA/EVM, rsync, Syncthing, Restic, Borg, Kopia, git-annex, casync.",
        "- Storage engines: RocksDB, LevelDB, Badger, Pebble, WiredTiger, SQLite, LMDB, FoundationDB, TiKV, raft-engine as adjacent source for WAL, LSM, page cache, checkpoints, object/tiered storage, and replicated logs.",
        "",
        "## Explicit Exclusions",
        "",
        "- GPFS/Spectrum Scale, WekaFS, PanFS, Quobyte and similar systems without complete public source.",
        "- Proprietary Windows NTFS/ReFS internals, WRK/leaked code, closed backup agents, closed cloud-drive clients.",
        "- Firmware blobs, kernel prebuilts, package payloads, ISO/VM/container images, object-store datasets, benchmark outputs.",
        "- Generic cloud SDKs, Kubernetes backup operators, UI wrappers, scheduler wrappers, and distro packaging recipes unless a patch changes source behavior relevant to filesystems.",
        "- Papers/blogs/PDFs as repository content. External documentation can be cited in notes, but the study corpus is source.",
        "",
        "## Study Order",
        "",
        "1. Linux VFS, page cache, block layer, and core local filesystems.",
        "2. Userspace mkfs/fsck/repair tools for ext/XFS/Btrfs/F2FS/EROFS/ZFS/bcachefs.",
        "3. xfstests, LTP, fio, blktests, pjdfstest for behavior and failure cases.",
        "4. FUSE, NFS, SMB/Samba, 9P, WebDAV and kernel/user protocol boundaries.",
        "5. CephFS, GlusterFS, Lustre, BeeGFS, HDFS, JuiceFS, SeaweedFS, Alluxio.",
        "6. BSD/illumos/Plan 9/ReactOS/Windows public source for cross-OS VFS comparison.",
        "7. Container, image, object-store, security/integrity/sync, and storage-engine adjacent code.",
        "",
    ]

    (DOCS / "source_repositories.md").write_text("\n".join(lines).rstrip() + "\n")


def write_fetch_manifest(rows: list[dict[str, str]]) -> None:
    out = DOCS / "source_fetch_manifest.tsv"
    with out.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["name", "url", "path", "tier", "category", "recurse", "default_count"])
        for row in rows:
            writer.writerow([
                row["id"],
                row["url"],
                row["path"],
                row["tier"],
                row["category"],
                row["recurse"],
                row["default_count"],
            ])


def write_gap_backlog() -> None:
    lines = [
        "# Source Gap Backlog",
        "",
        "This file records gaps that cannot be solved by adding a normal public Git",
        "repository, plus source families that are intentionally deferred.",
        "",
        "## No Complete Public Source",
        "",
        "- GPFS / IBM Spectrum Scale",
        "- WekaFS",
        "- PanFS / Panasas",
        "- Quobyte enterprise internals",
        "- Proprietary Windows NTFS/ReFS implementation",
        "- Closed cloud-drive clients and commercial backup agents",
        "- Vendor-only enterprise extensions for otherwise open projects",
        "",
        "Track these as unavailable public-source gaps. Do not invent mirror URLs,",
        "use leaked code, or count binary SDKs as source.",
        "",
        "## Non-Git Or Special Source Retrieval",
        "",
        "- `ecryptfs-utils`: canonical userspace source is Launchpad/Bazaar at",
        "  `https://code.launchpad.net/~ecryptfs/ecryptfs/trunk`. The GitHub mirror",
        "  in `manifests/sources.tsv` is operationally convenient, but the final",
        "  inventory should verify the Bazaar source with `brz`/`bzr` when this",
        "  project is studied in depth.",
        "- `curlftpfs`: SourceForge/CVS-era upstream should be verified before",
        "  treating any Git import as canonical.",
        "- `libtirpc` and `rpcbind`: canonical upstream is listed through",
        "  `git://linux-nfs.org/~steved/...` in `manifests/sources.tsv`. Some",
        "  networks block `git://`; if that happens, use distro mirrors such as",
        "  Debian Salsa only as read-only fallback source and record the",
        "  substitution in `metrics/remotes/remotes.lock.tsv`.",
        "",
        "## Deferred But Legitimate Source",
        "",
        "- More FUSE language bindings: llfuse, fuse-rs, macFUSE examples.",
        "- More historical filesystems: ocfs2-tools, gfs2-utils, hfsprogs and",
        "  additional APFS reverse-engineering projects.",
        "- More compression/archive primitives: zstd, xz, lz4, zlib, tar/cpio/pax.",
        "- More security/policy source: SELinux userspace, audit userspace, TPM",
        "  tooling, OpenSSL/libsodium/libgcrypt if crypto implementation auditing is",
        "  in scope.",
        "- More fuzzing: syzkaller and project-specific crash-consistency tests.",
        "",
        "## Case-Sensitive Filesystem Warning",
        "",
        "Large OS/kernel trees can contain paths that collide on case-insensitive",
        "macOS APFS. Clone Linux and cross-OS source trees on a case-sensitive APFS",
        "sparsebundle, Linux volume, or other case-sensitive filesystem when Git",
        "reports path conflicts.",
        "",
    ]
    (DOCS / "source-gap-backlog.md").write_text("\n".join(lines).rstrip() + "\n")


def write_inventory_template() -> None:
    lines = [
        "# Local Source Inventory",
        "",
        "No source inventory has been generated yet.",
        "",
        "Run:",
        "",
        "```sh",
        "cd /Users/wangweiyang/GitHub/learn_fs",
        "scripts/clone_sources.sh --tier required",
        "scripts/lock_remotes.sh",
        "scripts/verify_sources.sh --tier required",
        "scripts/source_inventory.py --tier required --assert-range",
        "```",
        "",
        "The generated inventory will replace this file with repository-by-repository",
        "line counts, local commit IDs, and missing checkout status.",
        "",
    ]
    path = DOCS / "local-source-inventory.md"
    if not path.exists():
        path.write_text("\n".join(lines))


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    rows = load_sources()
    write_target_repositories(rows)
    write_source_repositories(rows)
    write_fetch_manifest(rows)
    write_gap_backlog()
    write_inventory_template()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

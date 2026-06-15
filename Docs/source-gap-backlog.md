# Source Gap Backlog

This file records gaps that cannot be solved by adding a normal public Git
repository, plus source families that are intentionally deferred.

## No Complete Public Source

- GPFS / IBM Spectrum Scale
- WekaFS
- PanFS / Panasas
- Quobyte enterprise internals
- Proprietary Windows NTFS/ReFS implementation
- Closed cloud-drive clients and commercial backup agents
- Vendor-only enterprise extensions for otherwise open projects

Track these as unavailable public-source gaps. Do not invent mirror URLs,
use leaked code, or count binary SDKs as source.

## Non-Git Or Special Source Retrieval

- `ecryptfs-utils`: canonical userspace source is Launchpad/Bazaar at
  `https://code.launchpad.net/~ecryptfs/ecryptfs/trunk`. The GitHub mirror
  in `manifests/sources.tsv` is operationally convenient, but the final
  inventory should verify the Bazaar source with `brz`/`bzr` when this
  project is studied in depth.
- `curlftpfs`: SourceForge/CVS-era upstream should be verified before
  treating any Git import as canonical.
- `libtirpc` and `rpcbind`: canonical upstream is listed through
  `git://linux-nfs.org/~steved/...` in `manifests/sources.tsv`. Some
  networks block `git://`; if that happens, use distro mirrors such as
  Debian Salsa only as read-only fallback source and record the
  substitution in `metrics/remotes/remotes.lock.tsv`.

## Deferred But Legitimate Source

- More FUSE language bindings: llfuse, fuse-rs, macFUSE examples.
- More historical filesystems: ocfs2-tools, gfs2-utils, hfsprogs and
  additional APFS reverse-engineering projects.
- More compression/archive primitives: zstd, xz, lz4, zlib, tar/cpio/pax.
- More security/policy source: SELinux userspace, audit userspace, TPM
  tooling, OpenSSL/libsodium/libgcrypt if crypto implementation auditing is
  in scope.
- More fuzzing: syzkaller and project-specific crash-consistency tests.

## Case-Sensitive Filesystem Warning

Large OS/kernel trees can contain paths that collide on case-insensitive
macOS APFS. Clone Linux and cross-OS source trees on a case-sensitive APFS
sparsebundle, Linux volume, or other case-sensitive filesystem when Git
reports path conflicts.

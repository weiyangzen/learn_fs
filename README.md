# learn_fs

`learn_fs` is a source-only research workspace for file systems and
distributed file systems. It follows the same pattern as the existing
`learn_*` repositories in `/Users/wangweiyang/GitHub`, but the boundary is
broader: local filesystems, OS VFS layers, filesystem tools, FUSE/user-mode
filesystems, NFS/SMB/WebDAV, distributed and parallel filesystems, object-store
adjacent systems, container/virtualized storage, security/integrity, sync and
backup systems, tests, and selected storage-engine source.

The rule is strict: study source code. Do not count papers, blogs, docs sites,
binary release payloads, firmware blobs, VM/container images, benchmark output
datasets, leaked source, closed product internals, or proprietary-only SDKs as
part of this corpus.

## Where To Start

- [Docs/source_repositories.md](Docs/source_repositories.md) is the human
  overview and study order.
- [Docs/target-repositories.md](Docs/target-repositories.md) is the generated
  full source table grouped by category.
- [manifests/sources.tsv](manifests/sources.tsv) is the canonical
  machine-readable checkout manifest.
- [manifests/focus_paths.tsv](manifests/focus_paths.tsv) lists source paths to
  read/count first inside every repository.
- [Docs/source-gap-backlog.md](Docs/source-gap-backlog.md) records closed-source
  gaps and special retrieval caveats.
- [Docs/fs-language-priority-analysis.md](Docs/fs-language-priority-analysis.md)
  records the C/C++/Rust/Go judgment, FS level labels, OS fit, and
  deduplication policy.
- [Docs/optimized-research-targets.md](Docs/optimized-research-targets.md) is
  the deduplicated first-pass source set.
- [Docs/optimized-local-source-inventory.md](Docs/optimized-local-source-inventory.md)
  is the current measured LOC report for that optimized set.
- [artifacts/debate10/summary.md](artifacts/debate10/summary.md) records the
  ten-slice debate synthesis that produced the final boundary.

[Docs/source_fetch_manifest.tsv](Docs/source_fetch_manifest.tsv) is generated
from `manifests/sources.tsv` for auditing. Do not edit it by hand.

## Tiers

- `required`: default corpus for the first complete clone and reading pass.
- `important`: part of the full public-source boundary, cloned after the
  required set or when the current LOC/disk budget allows it.
- `adjacent`: useful source for design contrast; keep it in scope, but do not
  let it displace core filesystem source when the 200M-line ceiling is tight.

The full manifest currently has 214 repositories: 59 `required`, 119
`important`, and 36 `adjacent`. 144 repositories are marked
`default_count=yes` for the broad source LOC gate.

The deduplicated first-pass set has 57 repositories. It keeps OS/VFS,
local-FS/tooling, FUSE/NFS/SMB protocol boundaries, major distributed FS
implementations, object-store-adjacent backends, and validation tools while
deferring duplicate maintainer trees, language bindings, control-plane-only
repos, and storage engines. The current sparse focus-path checkout measures
21,263,025 code-like lines.

## Commands

From this directory:

```sh
scripts/verify_sources.sh --tier all --remote-only
scripts/verify_sources.sh --tier required --allow-missing
scripts/generate_research_targets.py
scripts/clone_optimized_focus.sh --jobs 2
scripts/lock_remotes.sh
scripts/verify_sources.sh --tier all --allow-missing
scripts/source_inventory.py --tier all --target-set optimized --scope focus-paths --csv metrics/loc/optimized-focus/by-repo.csv --json metrics/loc/optimized-focus/by-repo.json --markdown Docs/optimized-local-source-inventory.md --assert-range
```

Useful variants:

```sh
scripts/clone_sources.sh --tier important
scripts/source_inventory.py --tier important --scope focus-paths --assert-range
scripts/source_inventory.py --tier important --scope full-repo --csv metrics/loc/full-repo/by-repo.csv --json metrics/loc/full-repo/by-repo.json --markdown metrics/loc/full-repo/inventory.md
scripts/clone_optimized_focus.sh --dry-run
scripts/generate_docs.py
```

## Line-Count Policy

The target corpus size is 20,000,000 to 200,000,000 code-like lines.

`source_inventory.py` has two scopes:

- `focus-paths`: default. Counts the filesystem-relevant paths in
  `manifests/focus_paths.tsv`, excluding generated/vendor/build/doc output.
- `full-repo`: counts source-like files across each selected checkout after
  the same generated/vendor/build exclusions.

Use `focus-paths` as the primary gate. Use `full-repo` as a secondary audit so
large monorepos such as QEMU, Hadoop, FreeBSD, Linux, DAOS, Ceph, and
containerd do not hide the filesystem signal behind unrelated source.

## Disk And Filesystem Notes

The default clone script uses shallow partial clones:

```sh
git clone --depth=1 --filter=blob:none
```

Some large repositories still need substantial disk and network time. Large
kernel/OS trees can also contain paths that collide on case-insensitive macOS
APFS. If Git reports path conflicts, clone the source trees on a case-sensitive
APFS sparsebundle, Linux filesystem, or another case-sensitive volume.

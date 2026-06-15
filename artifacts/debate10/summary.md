# learn_fs 10-Agent Debate Summary

Generated: 2026-06-15

The user requested a `learn_fs` workspace under `/Users/wangweiyang/GitHub`,
with standards matching or exceeding `learn_compiler`, `learn_chromium`,
`learn_aosp`, and `learn_archlinux`, and with a source-only corpus in the
20,000,000 to 200,000,000 line range.

## Debate Coverage

The workflow used ten slices:

1. Linux VFS, local filesystems, filesystem tools, and tests.
2. Distributed filesystems and object-store adjacent storage.
3. FUSE, userspace filesystems, NFS, SMB, and network protocols.
4. COW filesystems, storage pools, device-mapper, ZFS, Btrfs, bcachefs.
5. Filesystem-adjacent storage engines.
6. Cross-OS VFS implementations and public Windows substitutes.
7. Cloud-native, container, virtualized, CSI, and block/NBD/SPDK storage.
8. Filesystem test, validation, benchmark, fault-injection, and repair tools.
9. Security, integrity, encrypted filesystems, sync, backup, and versioned trees.
10. Final verifier/synthesizer.

The candidate outputs are kept under `artifacts/debate10/run_*` when they were
written as standalone files. Some agent-specific files are also retained under
`Docs/` because they are useful detailed slices.

## Final Synthesis

The authoritative source boundary is no longer any single candidate file. It is:

- `manifests/sources.tsv`
- `manifests/focus_paths.tsv`
- generated docs in `Docs/source_repositories.md` and
  `Docs/target-repositories.md`

The manifest includes required, important, and adjacent tiers. This preserves
the "complete, no hidden omission" boundary while allowing local clone passes
to remain practical and line-count bounded.

## Verification State

Completed locally:

- Final manifest synthesis contains 214 repositories: 59 required, 119
  important, 36 adjacent; 144 are default-counted for the source LOC gate.
- TSV column checks for `manifests/sources.tsv` and `manifests/focus_paths.tsv`.
- Duplicate ID/path checks for source manifest.
- Focus-path ID references checked against source manifest.
- Python syntax check for `scripts/source_inventory.py` and
  `scripts/generate_docs.py`.
- Remote URL validation for the full manifest with
  `scripts/verify_sources.sh --tier all --remote-only`. The verifier found
  broken GitHub placeholder mirrors for `libtirpc` and `rpcbind`; these were
  replaced with verified `git://linux-nfs.org/~steved/...` upstreams, and the
  full 214-repository remote pass now completes successfully.
- `scripts/verify_sources.sh --tier required --allow-missing` structural pass.
  Missing checkouts are allowed in this mode because large source trees have
  not been cloned yet.

Not completed locally:

- Full clone of all required repositories.
- Full line-count inventory, because the source trees are not yet present.

## Final Policy

- Source only: no papers, blogs, binary payloads, firmware blobs, VM/container
  images, package caches, release tarballs, or benchmark result datasets.
- Public source only: closed filesystems and proprietary internals are tracked
  as gaps, never substituted with leaks or binary SDKs.
- Do not duplicate giant repositories across categories. One checkout can
  satisfy multiple study slices.
- Count `focus-paths` and `full-repo` separately.
- Keep large OS/kernel trees on a case-sensitive filesystem when macOS APFS
  path collisions appear.

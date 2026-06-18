# File Research: sources/os/plan9/9front/sys/src/cmd/vac/file.c

Purpose: Implements the Vac filesystem object layer, mapping `VacFs`/`VacFile` operations onto Venti `VtFile` trees and Vac metadata blocks.

Key behavior:
- Defines the private `VacFile` with parent/child links, refcounts, cached `VacDir`, data `source`, directory metadata `msource`, read/write locks, dirty/removal state, and qid offset handling.
- Uses an upward metadata lock order: a file may lock its parent to synchronize directory metadata, avoiding parent-to-child lock acquisition.
- Opens roots through `_vacfileroot`, including a Fossil compatibility redirect for roots with an extra level of indirection.
- Provides path walking, child caching, `.`, `..`, refcounting, and lazy opening of child data/meta Venti files from directory entries.
- Implements reads, block-score lookup, entry extraction, size queries, and directory enumeration via `VacDirEnum`.
- Manages directory metadata as a stream of sorted `MetaBlock`s: lookup, allocation, flush, remove, resize, and relocation on long rename.
- Supports mutation for create, write, truncate, set entries, set directory metadata, set qid space, remove, recursive flush, and sync.
- Opens existing Vac roots from `vac:` scores or score files, creates fresh Vac filesystems, writes new Venti root blocks, and preserves previous root score in `VtRoot.prev`.
- Includes helper `sha1matches` for block reuse and `vacfiledsize` for archive diff/extract code.

Dependencies:
- Uses `stdinc.h`, `vac.h`, `dat.h`, `fns.h`, `error.h`, Venti cache/file/block APIs, metadata pack/unpack helpers from `pack.c`, and Vac error strings.

Notable details:
- Directories are two Venti files: traditional directory entry stream plus metadata stream. Plain files are one Venti file.
- `vacfilegetid` returns qid plus accumulated qid offset so merged archives can avoid qid collisions.
- `vacfssync` flushes the whole tree, builds a three-entry root directory, writes a Venti root block, and updates `fs->score`.

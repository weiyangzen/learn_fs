# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildindex.c

Command-line utility to rebuild the Venti index from arenas, optionally rebuilding Bloom too.

Key behavior:
- `threadmain` parses `-b`, `-d`, `-i isect`, `-M imem`, and debug `-m`, initializes Venti config, forces arena parts read-only, allocates dcache, starts one index-section worker per selected `ISect`, and one arena-part worker per arena partition.
- `arenapartproc` scans arena clump directories in reverse clump order, reconstructs `IEntry` addresses, skips `VtCorruptType`, sends entries to the correct index section, and marks Bloom entries.
- Bucket mapping uses score hash divided by `ix->div`; helpers convert score, bucket, and section offset.
- `isectproc` performs a three-pass rebuild:
  1. receive entries and spill them into large sequential group buffers on the index partition;
  2. optionally redistribute group buffers into minibuffers using `IPool`;
  3. sort each minibuffer by packed entry ordering with address tie-breaks, then write final buckets.
- `sortminibuffer` compacts fragment-padded spill blocks, sorts entries, groups by bucket, writes `IBucket` blocks, and optionally zeroes bucket gaps.
- Memory sizing chooses group/minigroup counts and buffer size from `isectmem`, `MinBufSize`, and `MaxBufSize`.

Interactions:
- Reuses `buildbuck.c` comparison logic concepts but writes final disk buckets directly.
- Uses `readclumpinfos`, `packientry`, `packibucket`, `markbloomfilter`, and partition I/O.
- Updates global counters `arenaentries`, `skipentries`, and `indexentries`.

Notable details:
- Many invariants are enforced with `assert`/`sysfatal`; bucket overflow means “make index bigger”.
- `-d` forces all passes for debugging even when a single pass would fit.
- `-i` can rebuild only selected index sections.

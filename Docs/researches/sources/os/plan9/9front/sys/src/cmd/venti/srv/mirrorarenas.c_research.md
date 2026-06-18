# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/mirrorarenas.c

`mirrorarenas` mirrors one arena partition onto another while copying only data that has changed. It validates matching arena counts, names, versions, block sizes, and sizes before mirroring selected ranges or all arenas.

The copy logic writes header, new data region, optional sealed holes, clump directory blocks, arena tail, and sealed score. It can compute SHA1 while copying so sealed destination arenas preserve or verify the source seal. A write worker overlaps source reads with destination writes.

The tool is careful about append-only arena semantics: it refuses when destination is ahead of source, handles clumpmagic early to avoid header/tail disagreement, and reports seal mismatches rather than blindly accepting divergent sealed content. `-F` forces full copying; `-s` skips SHA1 verification.

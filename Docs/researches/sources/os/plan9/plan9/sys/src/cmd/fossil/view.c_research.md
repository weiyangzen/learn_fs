# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/view.c

This is an interactive Fossil/Venti tree viewer using Plan 9 draw/event APIs. It can open a local Fossil cache device/path or a `vac:<score>` root, decode headers, superblocks, labels, entries, pointer blocks, data blocks, metadata blocks, and directory entries, then present them as expandable UI nodes.

The storage side includes local partition address mapping (`PartSuper`, `PartLabel`, `PartData`), block reads via `pread`, label validation, global-score handling through Venti reads, and type/tag checking. The score formatter prints local addresses when possible and full Venti scores otherwise.

The visualization side builds `Tnode` trees lazily. Entries expand to sources, sources expand through pointer trees or data/metadata blocks, data blocks are heuristically decoded as `MetaBlock`, and metadata entries expand to decoded `DirEntry` fields.

The UI draws a simple text tree with plus/minus nubs. Left drag pans, right click toggles expansion, middle menu exits. The `-a` flag shows inactive entries.

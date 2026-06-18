# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenas.c

`printarenas` emits index-entry-style rows derived from arena clump directories. It loads a full Venti config, initializes enough disk cache, and iterates every arena or selected arena names.

`dumparena()` reads clump info in chunks, converts each `ClumpInfo` into an `IEntry` with logical index address, score, type, uncompressed size, and block count, then prints it. The output mirrors index entries reconstructed from arena truth.

This tool is useful for comparing arena contents to index contents or feeding external analysis around rebuild/check workflows.

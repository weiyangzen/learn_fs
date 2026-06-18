# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/srcload.c

This is a standalone stress/benchmark driver for Fossil `Source` trees. It opens a Fossil filesystem with `fsOpen`, dumps and counts the source tree, repeatedly creates and deletes random directory/file entries, prints stats, and measures total runtime.

The helper routines recursively create entries (`new`), recursively delete entries (`delete`), dump tree structure (`dump`), count descendants (`count`), and report top-level/max-depth statistics (`stats`). A dormant `bench` helper times repeated `sourceGetEntry` calls.

It depends directly on `fsOpen`, `Source` APIs, `Entry`, Venti formatting, and Plan 9 `Biobuf`. It looks like development/test code rather than production command code.

Compatibility note: calls such as `sourceOpen(s, ..., OReadWrite)` use a three-argument form, while `source.c` in this group defines `sourceOpen(Source*, ulong, int, int)`, suggesting this file may be stale relative to the current API or compiled with a wrapper/prototype elsewhere.

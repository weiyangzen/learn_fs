# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fns.h

Central function-prototype header for the Venti server and its utilities. It declares arena, arena-partition, index, index-section, clump, cache, Bloom, HTTP, graph, stats, config, parsing, disk-part, and formatting functions.

It exposes the main cross-file API: arena lifecycle and sync/writeback, index lookup/writeback, cache init/flush/kick, clump store/load, Bloom load/write/mark/test, config parsing, HTTP handlers, graph generation, part I/O, text-file parsing, raw conversion pack/unpack routines, and utility helpers.

It also defines common score copy/compare macros and allocation convenience macros. The sorted-by-name comment indicates the file is intended as a broad manual symbol index for this directory.

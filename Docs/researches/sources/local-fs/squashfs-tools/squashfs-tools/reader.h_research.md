# File Research: sources/local-fs/squashfs-tools/squashfs-tools/reader.h

Defines reader constants, readahead sizing/indexing, reader type ids, and `BLOCKS_MIN`. In single-reader builds it declares `readers_sane()`, otherwise provides an inline `TRUE`.

Defines `readahead`, `read_entry`, and `reader` structs used by `reader.c` and restore/status code. Exports reader/thread introspection and configuration APIs, sleep throttling, and minimum memory validation.

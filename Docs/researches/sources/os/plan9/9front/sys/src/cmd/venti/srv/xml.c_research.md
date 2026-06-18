# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.c

`xml.c` emits XML summaries for Venti arena maps, arenas, and indexes. `xmlarena()` writes arena attributes including partition, block size, range, timestamps, seal state, score, clump counts, data bytes, compressed bytes, and storage bytes.

`xmlindex()` writes index attributes, section maps, arena maps, and nested arena summaries. `xmlamap()` emits named start/stop ranges.

The file depends on XML primitive emitters declared in `xml.h` and implemented elsewhere in the HTTP layer. It is presentation glue for machine-readable index/storage status.

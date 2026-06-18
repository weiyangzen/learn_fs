# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/reseal.c

`reseal` rewrites the tail seal of sealed arenas in an arena partition. It parses the arena-part directory, selects named arenas, verifies the existing seal hash unless forced, repacks the tail in current format, writes the new score into the final tail block, and verifies again.

The verification path hashes the arena header/data/directory and final block with the score slot zeroed, matching Venti seal semantics. `-f` allows resealing despite an existing score mismatch; `-b` controls I/O buffer size; `-s` is parsed but not used in the active verification loop.

This is a repair/migration tool for arena tail encodings, especially when older encodings need a canonical freshly packed seal.

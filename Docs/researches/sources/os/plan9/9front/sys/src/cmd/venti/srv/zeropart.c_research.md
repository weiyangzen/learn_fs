# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/zeropart.c

`zeropart.c` provides `zeropart()`, which clears a `Part` from `PartBlank` to the end using a zeroed `ZBlock`. It writes full `MaxIoSize` chunks first and finishes with block-size chunks, then flushes and frees the buffer.

This helper is used by formatting tools to initialize arena/index/bloom partitions before writing headers and tables.

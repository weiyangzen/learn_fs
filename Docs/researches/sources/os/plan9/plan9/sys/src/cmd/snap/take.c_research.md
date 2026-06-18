# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/take.c

Process snapshot capture implementation.

Key behavior:
- Reads selected `/proc/<pid>` pseudo-files into `Data` blobs.
- Reads `/proc/<pid>/text` and memory segments from `/proc/<pid>/mem`.
- Parses `/proc/<pid>/segment` to discover segment names and address ranges.
- Splits text and memory into 1024-byte pages and deduplicates identical pages.
- Handles stack specially by using the saved register set to find the stack pointer and capture only live tail pages when possible.

Important details:
- Page deduplication uses a small checksum hash plus full byte comparison.
- All-zero pages are emitted as zero pages immediately.
- Uses libmach to decode the architecture-specific stack pointer from the register file.
- Warns but continues when individual `/proc` sections cannot be read.

Filesystem relevance:
- Direct: captures process state through Plan 9 `/proc` files and memory/text image files.

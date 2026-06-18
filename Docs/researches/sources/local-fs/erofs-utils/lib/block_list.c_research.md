# File Research: sources/local-fs/erofs-utils/lib/block_list.c

## Purpose
Implements optional block/source mapping output for tar/blob chunk workflows.

## Important Functions
- `erofs_blocklist_open()`: registers an output `FILE *` and whether source-map output is enabled.
- `erofs_blocklist_close()`: clears and returns the registered file pointer.
- `tarerofs_blocklist_write()`: writes block address, block count, source offset, and optional zeroed tail length.

## Behavior
- Writes nothing when no file is registered, block count is zero, or source-map mode is disabled.
- Formats values as hex block/source ranges for external tooling.

## Interactions
- Called from `blobchunk.c` when chunk index extents are serialized.

## Notes
The file contains a comment noting the interface needs cleanup.

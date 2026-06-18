# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_zstd.c

## Summary
Implements EROFS Zstd decompression with pooled stream workspaces.

## Main Responsibilities
- Allocates stream records.
- Validates Zstd config format and window log.
- Grows workspace allocation for larger dictionary/window sizes.
- Streams pages through the shared EROFS streaming decompressor helper.

## Key APIs
- `z_erofs_zstd_decomp`

## Important Behavior
The pool defaults to `num_possible_cpus()`. Config computes dictionary size from `windowlog + 10`, reallocates workspaces when needed, and tracks the maximum dictionary size globally.

## Risks
Workspace resizing temporarily isolates all streams and must restore pool availability correctly. Zstd stream errors are surfaced as textual reasons.

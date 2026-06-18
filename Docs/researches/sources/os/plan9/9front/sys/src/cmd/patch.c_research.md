# File Research: sources/os/plan9/9front/sys/src/cmd/patch.c

## Role

Applies unified diff patches.

## Parsing

`parse` scans for `---`/`+++` file headers and `@@` hunk headers. `fileheader` supports path component stripping and `/dev/null`. `hunkheader` parses old/new line numbers and counts, normalizing to zero-based offsets except for empty files.

Each hunk stores original text, old text, new text, paths, line counts, and source patch line number. Reverse mode swaps old/new paths, counts, offsets, and buffers after parsing. Hunks are sorted by old path and line.

## Applying

`apply` groups hunks by target file, slurps each file into memory with line-offset indexing, searches for hunk old text near the expected line with up to 250 lines of fuzz, appends unchanged and replacement text into a new output buffer, and schedules file replacement.

`blat` writes changes to temporary files, creates missing parent directories, handles `/dev/null` creation/deletion cases, and records pending changes. `finish` commits temp files by rename or removes them on failure/dry-run.

## Rejections

If a reject file is requested, failed hunks are written there in unified form and processing continues. Without a reject file, an unfound hunk is fatal.

## Options

Supports dry-run, reverse, path stripping, reject file, and changing working directory before applying.

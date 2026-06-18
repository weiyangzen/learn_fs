# File Research: sources/virtualization/nbd/treefiles.h

## Purpose
Declares treefile export constants and helper APIs.

## Main Contents
- `TREEDIRSIZE` is 1024 entries per directory level.
- `TREEPAGESIZE` is 4096 bytes per tree block file.
- Declares `construct_path()`, `delete_treefile()`, `mkdir_path()`, and `open_treefile()`.

## Dependencies
Includes pthread and sys/types declarations for mutex and `off_t`/mode usage.

## Risks and Notes
Treefile mode assumes 4KiB block granularity and directory fanout of 1024, which shapes export layout compatibility.

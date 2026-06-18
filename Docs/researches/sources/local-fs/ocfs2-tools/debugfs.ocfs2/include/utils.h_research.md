# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/utils.h

## Role

`utils.h` declares shared utility functions and helper structs used across `debugfs.ocfs2`.

## Data Types

It defines recursive dump options, a list-node wrapper for strings, and an enum selecting chain traversal behavior: dump group descriptors, dump free-bit summaries, or record free-bit summaries.

## API Coverage

The header declares feature-flag formatting helpers, journal flag formatting, nanosecond time formatting, pager helpers, inode/lockname/path translation, file dump/read helpers, permission/time string formatting, recursive dump, argument cleanup, contiguous free-bit analysis, debugfs path/file helpers, string-list operations, extent and chain traversal, and block-type detection.

## Role In Architecture

It is the shared support layer between command handlers, dump formatting, live debugfs readers, and recursive extraction.

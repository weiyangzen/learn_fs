# File Research: sources/os/linux/linux/fs/xfs/xfs_trace.c

## Purpose

`xfs_trace.c` instantiates XFS tracepoints. It includes the XFS headers needed by trace event definitions, then defines `CREATE_TRACE_POINTS` before including `xfs_trace.h`.

## Main Interfaces

- No callable functions are defined here.
- The key action is `#define CREATE_TRACE_POINTS` followed by `#include "xfs_trace.h"`, which causes tracepoint storage and event implementations to be generated once.

## Included Subsystems

The file includes headers for filesystem format, mount state, allocation, bmap, attributes, transactions, log internals, buffer items, quota and dquot items, log recovery, filestreams, fsmap, staged btrees, inode cache, unlinked inode items, AG state, error handling, iomap, in-memory buffers/btrees, exchange mappings/ranges, parent pointers, reverse mapping, refcount, metafiles, metadir, realtime groups, zoned allocation, health monitoring, failure notification, file operations, and generic filesystem error events.

## Dependencies and Callers

- Trace macros throughout XFS call events declared in `xfs_trace.h`; this file provides the single compilation unit that materializes them.
- The comment notes that `xfs_trace.h` is included last so helper definitions from prior headers are available to trace event implementations.

## Research Notes

- Changes to trace event definitions generally occur in `xfs_trace.h`, but this file must include any headers required by those definitions.
- Because this file creates tracepoints, duplicate `CREATE_TRACE_POINTS` definitions elsewhere would conflict.

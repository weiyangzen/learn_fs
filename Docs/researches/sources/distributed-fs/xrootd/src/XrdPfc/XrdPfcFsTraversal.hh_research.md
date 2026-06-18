# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.hh

## Purpose
Declares the filesystem traversal helper used to inspect the cache namespace through the XRootD OSS abstraction. It provides mutable traversal state that callers can consume while recursively walking directories.

## Important APIs, Types, and Functions
- `FilePairStat`: stores `stat` for a data file and its `.cinfo` partner plus `has_data`/`has_cinfo` flags.
- `begin_traversal`, `end_traversal`, `cd_down`, and `cd_up`: traversal lifecycle and navigation.
- `open_at_ro`, `unlink_at`, and `close_delete`: relative file operations against the current directory handle.
- Public buffers `m_current_dirs` and `m_current_files`: caller-visible results from the most recent slurp.
- `m_protected_top_dirs`: names skipped at root depth.

## Control Flow
The class is intentionally stateful: callers begin at a root, inspect the current buffers, descend using `cd_down`, and return with `cd_up`. When constructed with a `DirState` root, directory navigation mirrors into `m_dir_state`.

## State and Persistence Behavior
The class persists no data. It owns open directory handles during traversal and exposes current path/depth and current directory contents. `unlink_at` can delete files if callers choose to use it, so consumers must ensure purge/consistency policy before invoking it.

## Dependencies and Integration Points
Includes `XrdOssAt` for relative operations and `XrdOucEnv` for OSS calls. Forward-declared `DirState` allows integration with the resource monitor tree without making traversal own directory accounting.

## Risks and Test Signals
Because the result buffers are public and reused, consumers must copy/swap them before reentrant or out-of-band slurps. Tests should verify stack depth handling, current path formatting, relative open/unlink behavior, and correct `FilePairStat` pairing semantics.

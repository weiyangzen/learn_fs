# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.cc

## Purpose
Implements `FsTraversal`, a cache-local namespace walker used by resource monitoring and purge code. It opens directories through `XrdOss`/`XrdOssAt`, maintains current traversal state, identifies subdirectories, and pairs data files with matching `.cinfo` files.

## Important APIs, Types, and Functions
- Constructor stores the `XrdOss` reference and initializes `XrdOssAt`.
- `begin_traversal(DirState*, root_path)` enables DirState maintenance, then opens and slurps the root.
- `begin_traversal(root_path)` opens a root directory and initializes path/level/handle stack.
- `end_traversal()` closes all directory handles and clears traversal state.
- `cd_down()` opens a child directory relative to the current handle, updates path/depth, optionally advances `DirState`, and slurps entries.
- `cd_up()` closes the current handle and restores parent state.
- `slurp_dir_ll()` reads directory entries and populates `m_current_dirs` and `m_current_files`.

## Control Flow
Traversal is stack-based. `begin_traversal` opens the first directory and calls `slurp_current_dir`. Recursive callers consume `m_current_dirs`, call `cd_down`, process that directory, and call `cd_up`. `slurp_dir_ll` clears prior entry buffers, loops over `Readdir`, skips `.`/`..` and transient `-ENOENT`, skips configured protected top-level dirs at relative level zero, and groups non-directory names by stripping `.cinfo` extension into `FilePairStat`.

## State and Persistence Behavior
No persistent state is written. Runtime state includes directory handles, current path with trailing slash, relative depth, current file/dir vectors, optional `DirState` cursor, and protected top-level directory names. The walker reports observed `stat` metadata to callers but does not delete or modify files itself except through exposed `unlink_at`.

## Dependencies and Integration Points
Depends on `XrdPfcDirState`, `XrdPfc::Cache` trace access, `Info::s_infoExtension`, `XrdOss`, `XrdOssAt`, and `XrdOucEnv`. `ResourceMonitor` uses it for initial scans and out-of-band LFN checks; purge-related code can use `open_at_ro`/`unlink_at` helpers.

## Risks and Test Signals
Risks include relying on `StatRet`/`Readdir` behavior for file type and stat data, fixed 256-byte entry buffer, path erasure assumptions with trailing slashes, and unclosed handles if callers skip `end_traversal`. Tests should cover empty dirs, protected top dirs, files with data only, `.cinfo` only, matching pairs, nested traversal, and failed `Opendir`.

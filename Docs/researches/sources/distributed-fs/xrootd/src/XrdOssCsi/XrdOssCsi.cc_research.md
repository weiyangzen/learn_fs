# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.cc

Purpose: implements the top-level checksum-sidecar OSS wrapper. It hides checksum tag files from clients, creates `XrdOssCsiFile`/`XrdOssCsiDir` handlers, coordinates data-file operations with their tag files, and exports the plugin entry point.

Important APIs/functions: `newDir()` and `newFile()` wrap successor objects unless `tident` starts with `*`. `Init()` initializes config and scheduler. Directory `Opendir/Readdir` suppress tag paths. File-system operations reject direct tag-file paths. `Create()` ensures zero-length data files get matching empty tag files. `Unlink()` removes data and tag files under the per-file map lock. `Rename()` locks old/new tag map entries, renames data, creates destination tag directories, renames/unlinks tag files, and updates `pumap_`. `Truncate()` opens a CSI file and delegates `Ftruncate()`. `StatPF()` opens the file to report checksum verification bits.

State/persistence: persistent state is the data file plus tag file tree. In-memory map entries are shared through `XrdOssCsiFile::pumap_` to serialize open-file operations. `tagOpenEnv()` clones open environment, sets tag cgroup/space, and estimates allocation size for tag files.

Risks/test signals: rename/unlink recursion when map entries are stale, tag directory creation rollback, hidden tag paths, `StatPF` open cost, and consistency under concurrent opens. Tests should cover direct tag-file denial, create/truncate/open interactions, rename over existing files, missing tag files, and scheduler fallback when no scheduler is supplied.

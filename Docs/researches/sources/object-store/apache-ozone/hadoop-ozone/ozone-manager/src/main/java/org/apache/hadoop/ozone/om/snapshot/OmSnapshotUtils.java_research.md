# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotUtils.java

Purpose: `OmSnapshotUtils` contains filesystem utilities used by OM snapshot checkpoint and hardlink handling.

Important APIs and types: `truncateFileName(int, Path)` removes a leading path prefix. `getFileInodeAndLastModifiedTimeString(Path)` returns an inode/file-key plus modification-time identity string. `createHardLinkList(int, Map<Path, Path>)` writes a temporary text file describing hardlinks for tarball transfer. `linkFiles(File oldDir, File newDir)` recreates a directory tree using hardlinks for files.

Control flow: `createHardLinkList()` iterates link-target mappings, truncates both paths, strips active DB checkpoint paths down to filenames when the source begins with `OM_CHECKPOINT_DIR`, joins target and source with `HARDLINK_SEPARATOR`, and writes the accumulated UTF-8 content to a temp `data*.txt` file. `linkFiles()` walks the old directory, sorts relative paths so parents precede children, creates directories as needed, and uses `Files.createLink()` for files.

State and persistence behavior: methods create temporary link-list files, directories, and hardlinks. They do not modify OM DB metadata. Hardlink identity is filesystem-level state and may fail on filesystems that do not support hardlinks.

Dependencies and integration points: it uses `IOUtils.getINode`, Ozone constants for hardlink separators and checkpoint directory names, and Java NIO file APIs. It supports checkpoint servlet/tarball code and snapshot SST de-duplication workflows.

Risks: `truncateFileName()` assumes `truncateLength` is valid for every path. `linkFiles()` fails if destination entries already exist or if parent directories cannot be created. Hardlinks across filesystems are not supported. The hardlink list format is simple string serialization and depends on paths not containing the separator semantics unexpectedly.

Test signals: checkpoint servlet inode-based transfer tests and snapshot utility tests should cover hardlink list generation, active DB path stripping, and hardlink tree reproduction.

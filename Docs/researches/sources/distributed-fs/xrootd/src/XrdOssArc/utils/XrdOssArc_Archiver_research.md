# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Archiver

Purpose: Python utility invoked by archive backup workers to turn staged dataset split directories into one or more uncompressed zip archives and save them into a tape/MSS buffer or via an external saver command.

Important APIs/functions: `arcDirs(dsnDir)` validates contiguous `~1`, `~2`, ... source directories. `arcZip(arcDir, arcFN)` runs `zip -r -0` from inside each split directory, creates the archive in the parent directory, and chmods it read-only. `arcSave(tapDir, arcFN)` creates the target directory and copies the archive with metadata. `Main(argv)` parses `<dsnDir> <tapDir> <arcName> [copy_cmd]`, builds per-split archive names as `<base><n>-<count>.<ext>`, and either copies locally or runs `[copy_cmd, "save", tapDir] + arcList`.

State/persistence: creates/removes archive files in the dataset arena, writes archive copies under `tapDir`, and uses read-only mode as a completion marker. Debug behavior is controlled by `XRDOSSARC_DEBUG`; value greater than `1` sets `DKeep` but the variable is not used in this script.

Dependencies/integration: depends on system `zip`, Python `shutil`, `subprocess`, and XrdOssArc backup invocation. Risks include shell command construction for `zip`, archive names needing an extension, strict contiguous split numbering, and incomplete cleanup on failures. Tests should cover one/many split dirs, missing `~1`, zip return-code mapping, external saver failures, and path/name normalization.

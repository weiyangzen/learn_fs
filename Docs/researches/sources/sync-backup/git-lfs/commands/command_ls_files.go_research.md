<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ls_files.go -->
# sources/sync-backup/git-lfs/commands/command_ls_files.go

Purpose: implements `git lfs ls-files`, listing LFS pointer files from the index, current tree, specified refs/ranges, all history, or deleted entries, with text, debug, or JSON output.

Important APIs/types/functions: globals `longOIDs`, `lsFilesScanAll`, `lsFilesScanDeleted`, `lsFilesShowSize`, `lsFilesShowNameOnly`, `lsFilesJSON`, `debug`; `lsFilesObject`, `lsFilesCommand`, `fileExistsOfSize`, and `lsFilesMarker`; `lfs.GitScanner`.

Control flow: resolves optional ref/range or current ref/empty tree, sets OID display length, scans index when no args, then scans all history, deleted tree entries, range, or tree. Callback skips zero-size objects, de-duplicates by name for non-range/non-all scans, emits debug, JSON, or text output with checkout/download markers and optional size.

State and persistence behavior: read-only; checks working-tree file size and local LFS object existence for status markers. JSON output accumulates entries until scan completion.

Dependencies/integration points: integrates Git ref resolution, pointer scanning, filepath include/exclude filters, local filesystem decoding, and humanized sizes.

Risks and test signals: risks include `--all` argument ambiguity, name-based de-duplication hiding multiple historical OIDs, file-size-only checkout marker, and scan mode flag incompatibilities. Test signals include no-arg index+tree, explicit ref, range, all, deleted, JSON/debug/name-only/size/long output, include/exclude filters, and files absent from working tree.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_ls_files.go -->

# sources/sync-backup/bup/lib/bup/cmd/restore.py

## Purpose
`restore.py` extracts files and directories from a bup repository VFS into the filesystem, preserving metadata, optional sparse files, hardlinks, and configurable owner/group mappings.

## APIs and Control Flow
Important helpers are `valid_restore_path`, `parse_owner_mappings`, `apply_metadata`, `hardlink_compatible`, `hardlink_if_possible`, `write_file_content`, `write_file_content_sparsely`, and recursive `restore`. `main(argv)` parses remote/outdir/exclude/mapping options, opens a repository, resolves each requested path with metadata, follows `latest` links specially, and either restores children into the current directory or restores the leaf name. Directory restore creates paths, descends with `vfs.contents`, then applies metadata after children; file restore creates content, handles sparse writes and hardlink reuse, then applies metadata.

## State, Dependencies, Integration, Risks, Tests
Persistent state is the restored filesystem tree and metadata. Dependencies include `vfs`, `metadata` behavior through item metadata, `_helpers.write_sparsely`, owner mappings, `repo_for_location`, and exclude regex semantics shared with indexing. Risks include destructive overwrite/metadata application, path validation requiring branch and revision, hardlink compatibility false positives/negatives, sparse truncation correctness, symlink and special-file creation, and global `total_restored`. Test signals include latest handling, directory `.` semantics, owner map parsing, exclude behavior, sparse output, hardlink restoration order, metadata application timing, and outdir creation.

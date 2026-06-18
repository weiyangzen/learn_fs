# sources/sync-backup/borg/docs/usage/create.rst.inc

Purpose: generated reference for `borg create`, Borg's primary archive creation command.

Important APIs and control flow: accepts archive `NAME` and paths; supports dry-run, stats/JSON, item listing/filtering, stdin/content command input, externally supplied path lists, include/exclude rules, filesystem metadata toggles, files cache modes, file-change detection, `--read-special`, archive comments/timestamps/chunker/compression, hostname/username, and tags. Runtime recursively walks roots, applies slashdot prefix stripping, filters paths, chunks/hashes/compresses/encrypts content, writes metadata, and stores only new chunks.

State and persistence: creates archive metadata and data chunks in the repository and updates local caches for files/chunks. It stores extensive file metadata unless disabled.

Dependencies and integration points: pattern engine, files cache, chunker, compression help, placeholder expansion, metadata readers, stdin command execution, path-list parsing, and common options.

Risks: mtime cache modes can miss malicious or accidental timestamp rollback; inode-aware modes perform poorly on unstable network filesystems. Direct stdin piping can archive truncated output if producer fails; `--content-from-command` avoids that. `--one-file-system` mountpoint detection has Linux/macOS edge cases.

Test signals: archive creation with duplicate names, all files-cache modes, stdin and command input failure behavior, pattern ordering, metadata toggles, slashdot paths, list flags, JSON stats, and unchanged-file cache hits.

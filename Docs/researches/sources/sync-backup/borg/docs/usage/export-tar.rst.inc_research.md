# sources/sync-backup/borg/docs/usage/export-tar.rst.inc

Purpose: generated reference for `borg export-tar`, which writes an archive or selected paths as a tar stream/file.

Important APIs and control flow: accepts archive `NAME`, output `FILE` or `-`, optional path selectors, `--tar-filter`, `--list`, `--tar-format`, include/exclude patterns, and `--strip-components`. Auto filtering chooses gzip, bzip2, xz, zstd, or lz4 by filename extension.

State and persistence: read-only against Borg repository; writes tar output to a file, stdout, or filter pipeline.

Dependencies and integration points: tar writer, archive extraction selection, compression filter subprocesses, metadata serialization, pattern engine, and progress pass over metadata.

Risks: metadata preservation depends on tar format: BORG preserves all Borg-supported metadata, PAX preserves substantial POSIX/xattr data, GNU loses ACLs/xattrs/bsdflags and nanosecond precision. Sparse export is unsupported.

Test signals: tar output validity for BORG/PAX/GNU, auto filter selection, stdout mode, pattern/strip behavior, list output, and round-trip import where supported.

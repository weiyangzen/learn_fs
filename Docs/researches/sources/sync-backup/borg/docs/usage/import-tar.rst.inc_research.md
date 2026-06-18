# sources/sync-backup/borg/docs/usage/import-tar.rst.inc

Purpose: generated reference for `borg import-tar`, which creates a Borg archive from a tar stream/file.

Important APIs and control flow: accepts archive `NAME`, `TARFILE` or `-`, `--tar-filter`, stats/list/filter/JSON, `--ignore-zeros`, and archive options for comment, timestamp, chunker, and compression. Auto filtering detects compressed tar input by extension and runs the matching decompressor.

State and persistence: writes a new archive and chunks to the repository. It reads tar metadata and content from file, stdin, or a filter pipeline.

Dependencies and integration points: tar readers for BORG/PAX/GNU/ustar/V7/SunOS xattr formats, compression filter subprocesses, create-like archive options, repository encryption/passphrase flow, and stats/JSON output.

Risks: unlike `create`, this command does not support excluding files. Sparse import is unsupported. Concatenated tarballs require `--ignore-zeros` to skip end markers.

Test signals: imports from each supported tar format, stdin mode, auto and explicit filter modes, concatenated tar with ignore-zeros, JSON stats, metadata conservation compared with export-tar.

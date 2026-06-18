# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/uniq.c

Deduplicates a pipe-delimited account metadata file by username. It keeps the last line seen for each name, sorts records by name, and rewrites the file only if duplicates caused changes.

Used for maintaining `who`-style metadata files.

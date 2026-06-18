# File Research: sources/os/plan9/9front/sys/src/cmd/auth/uniq.c

Deduplicates auth who-style files keyed by the field before `|`.

Important behavior:
- Reads the whole file as lines.
- Splits each line at first `|`; the left side is `name`, right side is stored as `line`.
- If a name repeats, replaces the stored line with the later occurrence and marks the file changed.
- If any duplicate was found, sorts entries by name and rewrites the file as `name|line`.

Filesystem relevance:
- Mutates administrative auth files in place.
- If no duplicates are found, exits without rewriting, preserving file metadata/content.

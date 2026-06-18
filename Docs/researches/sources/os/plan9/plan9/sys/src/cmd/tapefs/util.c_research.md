# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/util.c

This file provides shared tapefs helpers for id maps and tree construction.

Key behavior:
- Reads passwd/group-style files into `Idmap` arrays.
- Maps numeric ids to names, falling back to decimal strings.
- Builds directory paths recursively from `Fileinf` records.
- Creates or updates `Ram` nodes and links them into parent directories.
- Looks up child entries by name.

Important details:
- Parent directories missing from an archive are synthesized with mode `0555|DMDIR`.
- Existing entries can be updated if a “new” record replaces metadata.
- File modes are forced to include at least user-read.
- Duplicate names with changed file/directory type are ignored with a warning.

Filesystem relevance:
- Direct: common metadata/tree layer for all tapefs backends.

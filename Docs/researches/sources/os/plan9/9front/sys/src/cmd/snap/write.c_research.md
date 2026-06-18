# File Research: sources/os/plan9/9front/sys/src/cmd/snap/write.c

Purpose: Serializes captured `Proc` snapshots into the custom snapshot file format.

Key data:
- `pfile[]`: maps proc-file enum entries to `/proc` file names.

Key routines:
- `writeseg`: writes segment offset/length followed by per-page records. Already-written pages become references (`m` or `t` plus pid/offset), zero pages become `z`, and new pages become raw `r` followed by bytes.
- `writesnap`: writes all captured proc-file data, optional text segment, and memory segment list for one process.

Integration: Paired with `read.c`; deduplication metadata set here is later used for page references.

Risks:
- Serialization mutates `Page` objects by marking them written and setting type/pid/offset.
- Output format relies on fixed-width decimal fields and single-character page tags.

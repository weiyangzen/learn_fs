# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/record.c

## Role

`record.c` implements persistent resume records for `defragfs.ocfs2`.

## Storage Format

The record file defaults to `/tmp/.ocfs2.defrag.record`. It stores the fixed header portion of `struct resume_record`, then null-terminated target paths, then a checksum over the preceding bytes. The maximum record size is 2 MiB.

## Operations

It can fill records from argv, move list ownership between records, dump the reconstructed command, store records with `fsync()`, validate checksums on load, rebuild argv-node lists, free records/nodes, and remove the record file after completion.

## Risk Areas

`free_record()` iterates while deleting list entries with `list_for_each`, which is unsafe compared with the safe variant used elsewhere. The on-disk format embeds native integer and struct layout assumptions, so it is intended for same-host resume rather than durable interchange.

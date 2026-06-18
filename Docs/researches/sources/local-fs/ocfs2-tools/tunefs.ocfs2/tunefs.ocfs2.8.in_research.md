# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/tunefs.ocfs2.8.in

## Role

Manual page template for `tunefs.ocfs2(8)`. It documents the command synopsis, operational expectations, options, query format specifiers, example usage, related tools, and copyright.

## Documented Behavior

The description says `tunefs.ocfs2` adjusts OCFS2 filesystem parameters on disk and expects the cluster to be online so it can take appropriate cluster locks for safe writes.

Documented options include:

- `--cloned-volume[=new-label]`
- `--fs-features=[no]feature...`
- `-J/--journal-options`
- `-L/--label`
- `-N/--node-slots`
- `-S/--volume-size`
- `-Q/--query`
- `-q/--quiet`
- `-U/--uuid-reset[=new-uuid]`
- `-v/--verbose`
- `-V/--version`
- `-y/--yes`
- `-n/--no`
- `--backup-super`
- `--list-sparse`
- `--update-cluster-stack`
- resize trailing `blocks-count`

The query section documents the same custom specifiers implemented in `op_query.c`: `B`, `T`, `N`, `R`, `Y`, `P`, `V`, `U`, `M`, `H`, and `O`.

## Important Warnings

The manual warns that `--cloned-volume` does not clone a volume; it only changes UUID/label so a clone can be mounted near the original.

The UUID reset section warns that duplicate UUIDs can cause erratic behavior or filesystem corruption.

The cluster stack section points users who want to update on-disk cluster stack without starting the new cluster toward `o2cluster(8)`.

## Consistency Notes

- The manpage documents `-N` valid range as 1 to 255, but the implementation allows larger counts when the filesystem uses the extended slot map.
- The synopsis does not mention the quota sync interval options implemented in `op_set_quota_sync_interval.c`.
- The synopsis includes short option cluster `-ipqnSUvVy`; implementation also has long-only progress and several long-only operations.

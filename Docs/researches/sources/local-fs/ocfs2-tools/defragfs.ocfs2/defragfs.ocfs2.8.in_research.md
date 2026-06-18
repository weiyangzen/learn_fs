# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/defragfs.ocfs2.8.in

## Role

This is the manual page template for `defragfs.ocfs2`, the online defragmenter for OCFS2 filesystems.

## Documented Interface

It documents targets as regular files, directories, or mounted OCFS2 block devices. Directory targets recursively process files; device targets resolve the mount point and process that tree.

Options include:

- `-c` count files that should be processed.
- `-v` verbose/stat-only detail mode.
- `-l` low I/O mode.
- `-g` resume recorded progress.
- `-h` help.

## Notes

The page states that `lost+found` is skipped, other device mount points are not crossed, active-file defrag is discouraged due to DLM lock contention, and fragmented or insufficient free space can limit improvement.

## Mismatch

The man page says `-v` never defragments the target, but the implementation treats `-v` as detail output and still performs defrag unless combined with other behavior.

# File Research: sources/os/plan9/9front/sys/src/cmd/skelfs.c

Purpose: Minimal synthetic 9P filesystem that presents a dynamically named skeleton file or directory.

Model:
- Per-fid `Skel` holds selected name and mode.
- Qid path encodes session and one of root, intermediate dir, or skeleton node.
- First walk from root captures the walked name unless mode is `'e'`.
- `step` computes qids and stat data for root, directory, and skeleton entries.
- `dirgen` exposes at most one child.
- Read-only opens only; reads are directory reads.

Options:
- `-D` chatty 9P.
- `-s service` post service.
- `-i` serve on stdio.
- `-t mode` default skeleton mode: file, directory, or empty-like behavior.
- Optional mount point defaults to `/mnt/skel`.

Integration: Uses lib9p helpers `walkandclone`, `postmountsrv`, and `srv`.

Risks:
- Per-fid name state means different walks can produce different skeleton names.
- File contents are always empty.

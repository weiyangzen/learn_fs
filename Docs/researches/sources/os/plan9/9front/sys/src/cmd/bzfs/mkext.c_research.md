# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/mkext.c

Despite the filename, this is the main `bzfs` loader for a bzip2/BLZ-compressed mkfs archive filesystem.

Behavior:
- Archive format is described as `bzfilesystem\n` prefix, bzip2 data, BLZ data, and trailing zero padding.
- Starts an in-memory ramfs mounted at a target mountpoint, default `/root`.
- Scans the input file on 512-byte boundaries for `bzfilesystem\n`.
- Uses `blockread` to bridge block-aligned devices to arbitrary byte reads through a pipe.
- Chains decompression as `blockread -> unbzip -> unbflz`.
- Reads mkfs-style file headers with six fields: name, mode, uid, gid, mtime, bytes.
- Creates directories/files under `mtpt`, writes contents, and sets metadata with `dirfwstat`.

Filesystem relevance:
- Provides a read-in, memory-resident boot filesystem intended for floppy/contiguous DOS-file use.
- Changes after load stay in RAM and are not written back.

Risks and caveats:
- Always takes the search path because of `if(1 || strstr(file, "disk"))`.
- `blockread` detects an all-zero 512-byte block using `memcmp(zero, blk, n) == n`, which is unusual since `memcmp` returns zero on equality.
- Fatal `error` exits with status `0`, matching historical Plan 9 conventions poorly for failures.

# File Research: sources/virtualization/libguestfs/lib/readdir.c

Implements `guestfs_readdir` by decoding daemon-produced XDR dirents.

Important behavior:
- Creates a temporary file path, calls `guestfs_internal_readdir(dir, tmpfn)`, and opens the result locally.
- Determines file size, then decodes `guestfs_int_dirent` records until XDR position reaches EOF.
- Grows the result array by doubling and checks for integer overflow.
- Transfers decoded name ownership into public `guestfs_dirent` entries.
- Frees partial results on error and unlinks the temporary file in all cases.

Filesystem relevance:
- Bridges appliance directory enumeration into host-side public dirent structures.

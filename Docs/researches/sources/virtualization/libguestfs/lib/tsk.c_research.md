# File Research: sources/virtualization/libguestfs/lib/tsk.c

Host-side wrappers for Sleuth Kit filesystem walk results.

Important behavior:
- `guestfs_impl_filesystem_walk` and `guestfs_impl_find_inode` ask the daemon to write XDR records into a temporary file.
- Parses that temp file into `guestfs_tsk_dirent_list`.
- Result arrays start at length 8 and double as needed.
- Each entry is zeroed before XDR decoding so xdr allocation behavior is correct.
- Final list length is set to the decoded entry count.
- Parse errors free partial result lists.

Filesystem relevance:
- Converts inode/filesystem walk data from the appliance into host-side structures for forensic-style filesystem traversal.

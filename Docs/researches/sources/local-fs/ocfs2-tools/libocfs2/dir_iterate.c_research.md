# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.c

Directory iteration engine for OCFS2 userspace.

`ocfs2_dir_iterate2()` validates the inode is a directory, prepares a `dir_context`, reads and preserves the dinode, then iterates either inline directory data or normal extent blocks. `ocfs2_dir_iterate()` is a compatibility wrapper translating the callback signature.

`ocfs2_process_dir_entry()` validates record length/alignment/name length, optionally skips trailers, empty entries, dot entries, or includes removed entries depending on flags, invokes the user callback, tracks changed/abort flags, and can scan deleted-entry slack when requested. Changed blocks are written back through `ocfs2_write_inode()` for inline dirs or `ocfs2_write_dir_block()` for normal blocks.

DX helpers iterate indexed-directory entry lists. `ocfs2_dx_entries_iterate()` handles inline DX roots directly or walks DX root extents and reads each DX leaf. `ocfs2_dx_frees_iterate()` follows the indexed directory free-block chain through directory trailers.

Debug mode opens a filesystem and prints directory entry inode/name pairs for a selected inode.

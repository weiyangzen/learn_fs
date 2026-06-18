# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vss.c

Implements SMB Volume Shadow Copy Service support for ZFS-style snapshots exposed through Windows `@GMT-YYYY.MM.DD-HH.MM.SS` tokens.

`smb_vss_enum_snapshots` handles `FSCTL_SRV_ENUMERATE_SNAPSHOTS` responses. It requires at least the 16-byte count response size, derives the mounted dataset path for the open file, and either returns only the snapshot count or queries and encodes a token list. Count/list/map operations are delegated to smbd through door upcalls. Encoded responses include returned count, token count, byte size, each GMT token in ASCII/Unicode form, and a final Unicode null for compatibility.

`smb_vss_lookup_nodes` resolves an active node to the corresponding node inside a requested snapshot. SMB1 supplies a GMT token string; SMB2+ uses the request timewarp timestamp. The function gets the current node mount path, maps the token/time to a snapshot name, obtains the filesystem root vnode, and calls `smb_vss_lookup_node`.

`smb_vss_lookup_node` builds `.zfs/snapshot/<snapname>/<relative path from fsroot to node>`, looks up the vnode under the filesystem root, and wraps it in an `smb_node_t`. It returns `ENOENT` if no corresponding snapshot node exists.

Token parsing helpers validate the exact `@GMT-NNNN.NN.NN-NN.NN.NN` format, find tokens in paths, extract the first token, and remove it from the original path so normal lookup proceeds against the non-token path. `smb_vss_extract_gmttoken` copies the fixed-size token into the caller buffer, null terminates it, removes it from the path, and returns `ENOENT` when no token is present.

The file depends on SMB door/XDR types for snapshot count/list/name mapping and assumes `.zfs/snapshot` layout for actual vnode lookup.

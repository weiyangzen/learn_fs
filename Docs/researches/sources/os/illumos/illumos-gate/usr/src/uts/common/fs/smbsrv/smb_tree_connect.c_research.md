# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree_connect.c

SMB1 protocol wrappers for tree connect, tree connect AndX, and tree disconnect. This file handles wire decode/encode and maps core tree statuses to legacy SMB errors, while `smb_tree.c` owns actual share connection logic.

`smb_tcon_puterror` translates core NT statuses into protocol-specific error classes/codes, including `ERRinvnetname`, `ERRaccess`, `ERROR_BAD_DEV_TYPE`, and generic server error.

`SMB_COM_TREE_CONNECT` pre-decodes path/password/service strings from the data block, initializes tree-connect arguments, starts DTrace probes, calls `smb_tree_connect`, and on success returns word count 2 with max buffer size and assigned TID.

`SMB_COM_TREE_CONNECT_ANDX` pre-decodes AndX command/offset, flags, password length and password bytes, path, and service. The command optionally disconnects the incoming TID first when `SMB_TCONX_DISCONECT_TID` is set, ignoring disconnect errors as required. It then connects the requested share, derives returned service string by tree type, and encodes one of three response formats: pre-NT dialect, NT dialect normal response, or extended response containing optional support, maximal access, and guest access.

`SMB_COM_TREE_DISCONNECT` is special because dispatch suppresses normal UID lookup. The pre-handler explicitly looks up UID and TID. The command returns `ERRinvnid` if either is invalid, sets `user_cr`, disconnects the tree, cancels outstanding requests for that tree, and returns an empty result.

The file also wraps each command in matching DTrace start/done probes.

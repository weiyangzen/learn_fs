# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_create.c

This file implements legacy SMB1 create command front ends and funnels them into `smb_common_open` through `smb_common_create`. It handles `SMB_COM_CREATE`, `SMB_COM_CREATE_NEW`, and `SMB_COM_CREATE_TEMPORARY`.

Entry points are `smb_pre_create`, `smb_post_create`, `smb_com_create`, `smb_pre_create_new`, `smb_post_create_new`, `smb_com_create_new`, `smb_pre_create_temporary`, `smb_post_create_temporary`, `smb_com_create_temporary`, and `smb_common_create`.

The `pre` functions zero `sr->arg.open`, decode DOS attributes, modification time, and path data from the SMB request, set create disposition and options appropriate to the command, and emit DTrace start probes. `SMB_COM_CREATE` uses `FILE_OVERWRITE_IF` and forces `FILE_NON_DIRECTORY_FILE`; `SMB_COM_CREATE_NEW` uses `FILE_CREATE`; temporary create also uses `FILE_CREATE` but takes a directory path and later synthesizes a filename.

`smb_com_create` and `smb_com_create_new` call `smb_common_create` and encode a one-word response containing the FID. `smb_com_create_temporary` increments a static `tmp_id`, builds a name like `ttNNNNN.tmp`, replaces the request path with `directory\name`, calls `smb_common_create`, and returns both FID and generated name.

`smb_common_create` normalizes legacy create parameters. It converts nonzero and non-`UINT_MAX` local modification time to GMT, sets size to zero, uses compatibility read/write open mode, derives desired access and share access through `smb_omode_to_amask` and `smb_denymode_to_sharemode`, maps SMB1 oplock header flags to batch, exclusive, or none, calls `smb_common_open`, and then runs `smb1_oplock_acquire` when an oplock was requested and open succeeded. If no oplock is granted/requested, it clears the SMB header oplock flags before responding.

Integration notes: this file is protocol-front-end glue rather than filesystem logic. The static temporary-name counter is process-local and simple; collision behavior is delegated to the create path. Error reporting is handled by setting `smbsr_status` after `smb_common_open` returns a nonzero NT status.

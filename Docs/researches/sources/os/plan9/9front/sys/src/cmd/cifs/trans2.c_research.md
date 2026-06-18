# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/trans2.c

Implements SMB `SMB_COM_TRANSACTION2` helpers and file/filesystem/DFS Trans2 calls.

Internal helpers build Trans2 headers (`t2hdr`), set parameter/data offsets and counts (`pt2param`, `pt2data`), run the RPC (`t2rpc`), and position cursors on returned parameter/data blocks.

Directory enumeration is implemented by `T2findfirst` and `T2findnext`, parsing `SMB_FIND_FILE_FULL_DIRECTORY_INFO` into `FInfo` arrays and handling Windows quirks such as bad reported directory entry counts and Win95 timing sensitivity.

Metadata functions query path info in NT all-info or older standard formats, set path info, set file length through file information, and query filesystem volume/device/size information.

`T2getdfsreferral` sends DFS referral requests and parses referral versions 1, 2, and 3, including path/address string heaps, TTL defaults, flags, and domain-root versus normal referral forms.

Used by `main.c` for walk/stat/dirread/wstat, by `fs.c` for info files, and by `dfs.c` for DFS cache resolution.

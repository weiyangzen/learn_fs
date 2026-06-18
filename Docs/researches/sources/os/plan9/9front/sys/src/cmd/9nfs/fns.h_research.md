# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/fns.h

This header declares shared `9nfs` functions.

Key groups:
- Auth and mapping: `auth2unix`, `authhostowner`, `readunixidmaps`, `pair2idmap`, `id2name`, `name2id`.
- RPC: `rpcM2S`, `rpcS2M`, `rpcprint`, `server`, `error`, `garbage`.
- 9P/fids: `xmesg`, `newfid`, `setfid`, `putfid`, `clunkfid`, `fidtimer`.
- Namespace bridge: `xfroot`, `xfile`, `xfid`, `setuser`, `xfstat`, `xfopen`, `xfwalkcr`, `xp2fhandle`, `xpclear`.
- NFS conversion: `convM2sattr`, `dir2fattr`.
- Logging and utilities: `chat`, `clog`, `panic`, `strstore`, `strparse`, `listalloc`.

Important interactions:
- Included via `all.h`.
- Documents the subsystem boundary across multiple implementation files not all present in this group.

Research notes:
- The prototypes show that this group is a slice of a larger `9nfs` program, with RPC and mapping implementations elsewhere.

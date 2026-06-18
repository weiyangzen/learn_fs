# File Research: sources/os/linux/linux/fs/nfsd/xdr.h

`xdr.h` defines NFSv2 server-side XDR argument/result storage types and encoder/decoder prototypes. It is primarily a type contract between the NFSv2 RPC dispatch layer and XDR implementation code.

Core request structures include filehandle-only, setattr, dirop, read, write, create, rename, link, symlink, and readdir arguments. Result structures include simple status, attrstat, diropres, readlinkres, readres, readdirres, and statfsres.

`union nfsd_xdrstore` provides per-request scratch storage sized by `NFS2_SVC_XDRSIZE`. This lets the RPC service layer allocate enough argument/result memory without knowing each procedure’s specific type.

The header declares:
- NFSv2 decoders: fhandle, sattr, dirop, read, write, create, rename, link, symlink, readdir.
- NFSv2 encoders: stat, attrstat, diropres, readlink, read, statfs, readdir.
- Directory cookie and entry encoders.
- Release callbacks for responses holding filehandles or pages.
- Common helper functions for NFSv2 ACL code: filehandle decode, status encode, and fattr encode.

The structures retain NFSv2 constraints, such as 32-bit read/write offsets and simple directory cookies.

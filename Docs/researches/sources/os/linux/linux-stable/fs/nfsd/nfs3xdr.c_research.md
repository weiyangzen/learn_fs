# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3xdr.c

## Summary
NFSv3 XDR encode/decode support for NFSD procedures.

## Main APIs
Decoders cover filehandles, setattr, diropargs, access, read/write, create, mkdir, symlink, mknod, rename, link, readdir, readdirplus, and commit. Encoders cover all NFSv3 procedure results plus READDIR entry callbacks.

## Behavior
Decoding validates filehandle sizes, filename length and illegal bytes, setattr time modes, write payload length/count consistency, create modes, symlink payload placement, and mknod types. Encoding handles NFSv3 attributes, post-op attributes, weak cache consistency data, read/readlink page payloads, write verifiers, FSSTAT/FSINFO/PATHCONF fields, and COMMIT replies.

## Directory Encoding
READDIR and READDIRPLUS entries reserve cookie slots, later patched by `nfs3svc_encode_cookie3()`. READDIRPLUS composes per-entry filehandles only when lookup succeeds, the child is not a mountpoint, and inode numbers match.

## Risks
Manual XDR buffer sizing and page payload stitching are sensitive to off-by-one and too-small-buffer handling. Some FSSTAT/FSINFO/PATHCONF responses use a null filehandle to force empty post-op attrs after the procedure has released the input handle.

# File Research: sources/os/linux/linux/fs/nfsd/nfs3xdr.c

Read completely: 1356 lines.

NFSv3 XDR encode/decode implementation for core server arguments, results, attributes, weak cache consistency data, directory entries, and release helpers.

Key responsibilities:
- Encodes and decodes NFSv3 primitive types such as nfstime3, status, filehandles, cookie verifiers, write verifiers, filenames, directory operation arguments, setattr values, sattr guards, and device numbers.
- Encodes file attributes from `kstat`, including mode, uid/gid through the request user namespace, symlink size clamping, used bytes, rdev, fsid source selection, fileid, and atime/mtime/ctime.
- Encodes pre-op, post-op, and weak cache consistency data, including no-attribute cases for stale or negative filehandles.
- Decodes all NFSv3 procedure arguments: fhandle, setattr, diropargs, access, read, write, create, mkdir, symlink, mknod, rename, link, readdir, readdirplus, and commit.
- Encodes all NFSv3 procedure results: getattr, wccstat, lookup, access, readlink, read, write, create, rename, link, readdir, fsstat, fsinfo, pathconf, and commit.
- Handles page-backed opaque result payloads for READ, READLINK, and READDIR.
- Composes optional filehandles and attributes for READDIRPLUS entries, while suppressing mountpoint entries and export-root parent handles.
- Backfills directory cookies after the next offset is known.
- Provides release helpers for one- and two-filehandle result structures.

Important interactions:
- Depends on `fh_getattr`, `lease_get_mtime`, export fsid source logic, `fh_compose`, dcache lookup, and request result buffer/page management.
- READDIR entry encoders are callback-compatible with `nfsd_readdir`.

Notable risks:
- Filename decode rejects zero-length names, names longer than `NFS3_MAXNAMLEN`, embedded NUL, and slash.
- Manual XDR length/reservation and page payload accounting must remain exact to avoid malformed replies or buffer exhaustion.
- READDIRPLUS filehandle composition intentionally avoids returning handles for mountpoints and for `..` at filesystem/export roots.

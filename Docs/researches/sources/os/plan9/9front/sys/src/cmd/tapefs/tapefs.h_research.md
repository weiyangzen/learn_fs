# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tapefs.h

`tapefs.h` defines the shared ABI between the common `tapefs` 9P server and format-specific backends.

Contents:
- Endian helpers: little-endian `g2byte`, `g3byte`, `g4byte`; big-endian `b4byte`, `b8byte`.
- Common constants: open permission mask `OPERM` and max IO buffer `Maxbuf`.
- `Fid`: busy/open/remove-on-close state, fid number, user, current `Ram`.
- `Ram`: in-memory filesystem node with tree links, qid, mode, name, times, owner/group, archive address, data pointer, and size.
- Permission bit constants used by `perm`.
- `Idmap` maps numeric ids to names.
- `Fileinf` is the backend-neutral metadata record used to populate `Ram` nodes.

Externals/prototypes:
- Shared globals: root `ram`, current `user`, uid/gid maps, lazy directory flag `replete`, `blocksize`, and global qid path counter.
- Backend-required functions: `populate`, `dotrunc`, `docreate`, `doread`, `dowrite`, `dopermw`, `popdir`.
- Common helpers: allocation, id mapping, `poppath`, `popfile`, and lookup.

Risks:
- Backend interface assumes static/simple data lifetimes for `Fileinf` fields.
- `Ram.data` is untyped and backend-specific, so misuse is unchecked by the compiler.

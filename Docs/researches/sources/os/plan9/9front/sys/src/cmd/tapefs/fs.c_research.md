# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/fs.c

`fs.c` is the common 9P server core for `tapefs` archive/filesystem backends.

Responsibilities:
- Parses generic options for mountpoint, passwd/group maps, verbosity, old/new tap time handling, and block size.
- Creates the root `Ram`, calls backend `populate`, then forks an IO process and mounts a pipe-backed 9P service at `/n/tapefs` by default.
- Implements 9P handlers for version, auth, attach, walk, open, create, read, write, clunk, remove, stat, and wstat.
- Dispatches requests through `fcalls[]` and `io`, using `convM2S`/`convS2M`.

Semantics:
- Authentication is not required.
- Create/remove/wstat are denied by default.
- `perm` allows all non-write permissions and denies writes globally.
- Directory reads lazily call backend `popdir` if not replete and encode child `Ram` nodes with `ramstat`.
- File reads call backend `doread`; writes call backend `dowrite` only if `dopermw` permits.

Important structures:
- `Fid` tracks 9P fid state and current `Ram`.
- `Ram` represents in-memory tree nodes populated by backend adapters.

Risks:
- Manual fid reuse has a likely bug: `newfid` finds reusable `ff` but still allocates a new fid because it does not return after reinitializing `ff`.
- `blocksize` is declared twice in this file.
- The server is mostly read-only by policy; backend write hooks are present but unused for these adapters.

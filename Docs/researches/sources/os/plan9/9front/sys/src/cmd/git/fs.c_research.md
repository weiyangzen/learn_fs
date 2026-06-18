# File Research: sources/os/plan9/9front/sys/src/cmd/git/fs.c

9P filesystem view of a git repository.

Key responsibilities:
- Exposes root entries `HEAD`, `branch`, `object`, and `ctl`.
- Maps branches, commits, trees, blobs, tags, and object hashes into synthetic 9P directories/files.
- Provides commit metadata files: `tree`, `parent`, `msg`, `hash`, `author`, and `committer`.
- Generates stable synthetic qids with a small qid cache.
- Resolves refs, reads objects, follows symlinks within tree walks, and lists object directories.
- Implements lib9p attach, walk, clone, open, read, stat, and fid cleanup.

Important behavior:
- `ctl` reports current branch and repo root.
- Blob/tag reads return raw object data; tree/commit reads are directory listings.
- Branch refs are read from `.git/refs`; `HEAD` ref indirection is followed.
- `.git` path entries are hidden when walking object trees.

Notable risks:
- Symlink resolution avoids cycles by checking existing crumbs, but it is limited to in-tree object traversal.
- qid generation uses an in-memory cache and monotonically increasing qid ids; it is stable only within the running server.

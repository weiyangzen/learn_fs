# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/hgdb.c

Implements an experimental Mercurial debug/update/merge planning tool.

Key points:
- Loads `.hg/dirstate` to get parent hashes and tracked file state.
- Parses dirstate entries into a hash table keyed by path.
- Uses mounted `hgfs` revision trees to compare working parent, target revision, and common ancestor.
- Finds the target revision hash from `/mnt/hg/<rev>/rev`.
- Refuses updates with an outstanding merge parent.
- Uses `ancestor()` to locate common ancestor between current parent and target revision.
- Runs `/bin/derp` with selected options to compare left, right, and ancestor trees.
- Parses `derp` output and prints shell-like actions:
  - create directories
  - copy files
  - remove files
  - invoke `merge3` for conflicts
  - annotate delete conflicts or unknown states
- Option `-c` treats working directory as clean.
- `pjoin()` safely joins base paths and relative names.

Dependencies and interactions:
- Depends on a mounted `hgfs` namespace, `ancestor.c`, and external `/bin/derp`.
- Uses `getworkdir()`, `readhash()`, and hash formatting.

Research relevance:
- Not the 9P server itself, but a companion tool showing intended use of `hgfs` history views for update/merge planning.

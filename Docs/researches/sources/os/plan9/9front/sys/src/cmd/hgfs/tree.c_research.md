# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/tree.c

Builds manifest-derived revision trees for `hgfs`.

Key points:
- `nodepath()` reconstructs filesystem/store paths from `Revnode` ancestry.
- Supports Mercurial filename mangling for Windows-reserved names, uppercase letters, underscores, high bytes, and disallowed punctuation.
- `mknode()` allocates a tree node, optionally embedding hash bytes and name string.
- `addnode()` inserts manifest paths into a hierarchical tree, creating directory nodes as needed and updating ancestor path qid values.
- `loadmanifest()` parses manifest lines containing path, NUL, file hash, and mode byte.
- Can load a full manifest tree or filter to a hash table of changed paths.
- `loadfilestree()` builds the full file tree for a revision.
- `loadchangestree()` reads changed file names from a changelog entry, builds a hash table, then loads only matching manifest entries.
- `closerevtree()` refcounts and frees tree nodes, including historical `before` links.

Dependencies and interactions:
- Uses manifest revlog extraction through `revlogopentemp()`.
- Used by `fs.c` to serve `files` and `changes` directories.

Research relevance:
- Converts Mercurial manifest text into the directory hierarchy exposed through 9P.

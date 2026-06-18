# File Research: sources/os/plan9/9front/sys/src/cmd/git/save.c

Creates git tree and commit objects from the working tree and `.git/INDEX9`. It writes loose zlib-compressed objects with canonical git headers, maps Plan 9 file modes to git modes, builds tree objects recursively, and writes commit objects with supplied author/committer/date/message/parents.

`treeify` starts from the current `HEAD` tree or an empty tree, applies normalized path updates, respects tracked/removed states from the index, writes blobs for tracked files, deletes missing/removed entries, and preserves unchanged tree entries. It rejects modifying symlink and submodule entries. `main` parses metadata flags, loads and sorts the index, invokes `treeify`, emits a commit object, and prints the new hash.

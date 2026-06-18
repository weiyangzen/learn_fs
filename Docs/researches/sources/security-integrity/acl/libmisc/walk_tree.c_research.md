<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/walk_tree.c -->
# sources/security-integrity/acl/libmisc/walk_tree.c

Purpose: Recursive traversal engine shared by `getfacl` and `setfacl`. The file is 258 lines.

Important APIs and functions: Key symbols include `walk_tree_visited`, `walk_tree_rec`, `walk_tree`.

Control flow: Uses lstat/stat according to logical/physical flags, tracks visited `(dev, ino)` directories to break cycles, enforces one-filesystem mode, manages a limited pool of directory handles, and calls a user callback for each path or failure.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/walk_tree.c -->

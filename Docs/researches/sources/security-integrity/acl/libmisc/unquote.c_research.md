<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/unquote.c -->
# sources/security-integrity/acl/libmisc/unquote.c

Purpose: In-place unquoter for ACL text qualifiers. The file is 57 lines.

Important APIs and functions: Key symbols include `isoctal`.

Control flow: Walks quoted strings, decodes backslash escapes and octal byte forms, compacts the result in the same buffer, and returns the unquoted pointer.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/unquote.c -->

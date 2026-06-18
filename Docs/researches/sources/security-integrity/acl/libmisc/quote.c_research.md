<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/quote.c -->
# sources/security-integrity/acl/libmisc/quote.c

Purpose: Quotes strings for ACL text and diagnostics so control/special characters remain parseable. The file is 62 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: Scans for characters requiring escaping, allocates a string object, and emits backslash/octal escape sequences for unsafe bytes.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/quote.c -->

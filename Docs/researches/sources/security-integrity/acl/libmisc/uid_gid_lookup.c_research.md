<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/uid_gid_lookup.c -->
# sources/security-integrity/acl/libmisc/uid_gid_lookup.c

Purpose: Resolves textual ACL user/group qualifiers to numeric ids with robust buffer growth around reentrant passwd/group APIs. The file is 128 lines.

Important APIs and functions: Key symbols include `get_id`, `grow_buffer`, `__acl_get_uid`, `__acl_get_gid`.

Control flow: Handles numeric strings directly, calls `getpwnam_r`/`getgrnam_r`, retries on `ERANGE`, and returns ACL-style errors on misses.

State and persistence: State is caller-owned buffers, static lookup retry state, traversal stacks, directory-handle lists, or temporary quoted strings. These helpers do not persist ACLs themselves but shape parser/display/traversal behavior that later library calls persist.

Dependencies and integration points: Integrates with `misc.h`, libc allocation and stdio, passwd/group databases, directory and stat APIs, `walk_tree.h` flags, and the command-line tools' callback model.

Risks: Buffer growth and in-place unquoting are memory-safety sensitive. Name lookup must distinguish nonexistent names from transient errors. Tree walking must avoid symlink loops, descriptor exhaustion, path overflows, and accidental cross-filesystem traversal.

Test signals: Exercise long input lines, quoting/unquoting control characters, numeric and symbolic uid/gid lookup with preload fixtures, recursive walks under `-R/-L/-P`, descriptor-limit scenarios, symlink cycles, and path-length failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/uid_gid_lookup.c -->

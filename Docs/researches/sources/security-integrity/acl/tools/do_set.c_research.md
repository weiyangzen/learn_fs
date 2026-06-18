<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.c -->
# sources/security-integrity/acl/tools/do_set.c

Purpose: Core ACL mutation engine used by `setfacl` after command parsing. The file is 529 lines.

Important APIs and functions: Key symbols include `find_entry`, `has_execute_perms`, `clone_entry`, `print_test`, `set_perm`, `retrieve_acl`, `remove_extended_entries`, `do_set`, `RETRIEVE_ACL`.

Control flow: As a `walk_tree` callback, lazily retrieves access/default ACLs, applies command sequences, handles conditional execute `X`, replaces/removes entries, removes extended/default ACLs, clones base entries for default ACL creation, recalculates masks unless suppressed, validates results, prints test output or persists with `acl_set_file`/`acl_delete_def_file`.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/chacl.c -->
# sources/security-integrity/acl/tools/chacl.c

Purpose: Installed IRIX-compatible `chacl` tool for setting, removing, listing, and recursively applying access/default ACLs. The file is 354 lines.

Important APIs and functions: Key symbols include `acl_delete_file`, `list_acl`, `set_acl`, `walk_dir`, `usage`, `main`.

Control flow: Allows one mode flag, parses ACL text with `acl_from_text`, validates with `acl_check`, removes access/default ACLs by deleting extended entries or default xattrs, lists compact ACL text, and applies ACLs directly or through its recursive directory walker.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/chacl.c -->

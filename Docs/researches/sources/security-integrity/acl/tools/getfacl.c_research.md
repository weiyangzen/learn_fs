<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/getfacl.c -->
# sources/security-integrity/acl/tools/getfacl.c

Purpose: Installed `getfacl` command implementation for printing access/default ACLs, headers, effective-right comments, tabular output, recursion, symlink policy, numeric ids, and POSIXLY_CORRECT behavior. The file is 762 lines.

Important APIs and functions: Key symbols include `free_list`, `max_name_length`, `acl_perm_str`, `acl_mask_perm_str`, `apply_mask`, `show_line`, `do_show`, `acl_get_file_mode`, `flagstr`, `do_print`, `help`, `main`, `POSIXLY_CORRECT_STR`, `POSIXLY_CMD_LINE_OPTIONS`.

Control flow: Parses options, configures walk flags and output modes, walks command-line or stdin paths via `walk_tree`, reads access/default ACLs with fallback to mode-derived ACLs on unsupported filesystems, skips base ACLs when requested, strips leading slashes unless disabled, and formats output through `acl_to_any_text` or its tabular renderer.

State and persistence: Tool state is process-global option flags, parsed command sequences, traversal flags, current path/stat data, transient ACL handles, and accumulated exit status. Persistent effects occur when setters/delete helpers update ACL xattrs or chmod-compatible mode bits on visited files.

Dependencies and integration points: Integrates public libacl APIs, private libmisc quoting/lookup/walk helpers, gettext/locale, libc option parsing, `walk_tree` recursion semantics, and generated build rules from `tools/Makemodule.am`.

Risks: CLI behavior is user-visible and historically compatible: POSIXLY_CORRECT modes, symlink traversal, default ACL handling, mask recalculation, absolute-path stripping, and partial-error exit codes must remain stable. Mutation paths can broaden or narrow permissions if mask/default ACL logic regresses.

Test signals: Run `make check` tool cases plus manual `getfacl`/`setfacl`/`chacl` scenarios on files, directories, symlinks, recursive trees, named users/groups, numeric ids, stdin path lists, base-vs-extended ACLs, unsupported filesystems, and dry-run/test output.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/getfacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/copy-acl.c -->
# sources/security-integrity/acl/examples/copy-acl.c

Purpose: Example program copying access and default ACLs from one source path to one or more destination paths. The file is 70 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `main`.

Control flow: Parses argv, reads source access/default ACLs with `acl_get_file`, loops over destinations applying both with `acl_set_file`, reports per-destination failures, and frees both ACL handles.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/copy-acl.c -->

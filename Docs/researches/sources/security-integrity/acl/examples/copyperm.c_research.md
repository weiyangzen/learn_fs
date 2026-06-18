<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/copyperm.c -->
# sources/security-integrity/acl/examples/copyperm.c

Purpose: Example program showing cp-style permission preservation through libacl's `perm_copy_file` API and libattr error context callbacks. The file is 61 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `error`, `main`.

Control flow: Initializes locale, validates `from to` arguments, provides an `error_context` printer, calls `perm_copy_file`, and exits by the helper's status.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/copyperm.c -->

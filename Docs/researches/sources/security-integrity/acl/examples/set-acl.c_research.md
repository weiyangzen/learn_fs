<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/set-acl.c -->
# sources/security-integrity/acl/examples/set-acl.c

Purpose: Example implementation of a small setfacl-like writer for access ACLs. The file is 64 lines and is intended as sample code rather than the primary installed tool implementation.

Important APIs and functions: Key symbols include `main`.

Control flow: Parses an ACL text argument, validates it with `acl_valid`, applies it to each remaining path with `acl_set_file`, reports failures, and frees the ACL.

State and persistence: Runtime state is argv-derived paths, transient `acl_t` handles, text buffers, and return status. Persistence occurs only when the example calls `acl_set_file` or permission-copy helpers against destination files.

Dependencies and integration points: Depends on public `sys/acl.h` and/or `acl/libacl.h`, libc diagnostics, optional libattr error-context support, and the installed libacl ABI that downstream users are expected to call similarly.

Risks: The examples have intentionally simple error handling and do not cover every production edge case, such as non-directory default ACL behavior or partial destination failures. They still exercise real filesystem ACL writes, so they should be run only on disposable files.

Test signals: Compile examples against installed headers, run them on temporary files/directories with base and extended ACLs, verify output with `getfacl`, and check failure handling for invalid ACL text or unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/set-acl.c -->

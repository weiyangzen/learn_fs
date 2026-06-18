# sources/security-integrity/selinux/libsemanage/example/test_fcontext.c

Purpose: provides a small example program that creates a local file-context mapping through the libsemanage public API. It demonstrates handle creation, access checking, connection, fcontext key construction, existence checking, record creation, context parsing, and local modification.

Important APIs/types/functions: uses `semanage_handle_create`, `semanage_access_check`, `semanage_connect`, `semanage_fcontext_key_create`, `semanage_fcontext_exists`, `semanage_fcontext_create`, `semanage_context_from_string`, `semanage_fcontext_set_con`, `semanage_fcontext_set_type`, and `semanage_fcontext_modify_local`.

Control flow: `main` expects a context string in `argv[1]` and a path expression in `argv[2]`, connects to semanage, rejects an already-existing regular-file mapping, builds a new fcontext record, assigns the parsed context, and stores it in the local database.

State and persistence behavior: it writes only the local fcontext customization cache; there is no explicit `semanage_begin_transaction` or `semanage_commit`, so as an example it is incomplete for durable installation on many backends. It frees the fcontext key and record on the success path but leaks the handle and context.

Dependencies and integration points: includes public libsemanage headers and `sepol/sepol.h`. It is useful as an API smoke example for file-context operations and mirrors command-line `semanage fcontext -a` behavior at a low level.

Risks: no `argc` validation before indexing `argv[1]`/`argv[2]`, incomplete cleanup on most error paths, no disconnect/destroy, no commit, and hard-coded regular-file type. Test signals are successful duplicate detection, context-string parsing failures, local fcontext query after commit when completed, and sanitizer warnings for argument misuse or leaks.

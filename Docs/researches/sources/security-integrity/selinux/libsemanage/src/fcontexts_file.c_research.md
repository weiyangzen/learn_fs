# sources/security-integrity/selinux/libsemanage/src/fcontexts_file.c

Purpose: provides the text-file backend for file-context records. It translates between `file_contexts.local` style lines and `semanage_fcontext_t` records for `dbase_file`.

Important APIs/functions: `type_str` maps internal fcontext type constants to file-context tokens; `fcontext_print` emits expression, type token, and either a context string or `<<none>>`; `fcontext_parse` parses one non-comment record; `SEMANAGE_FCONTEXT_FILE_RTABLE` registers parser/printer; `fcontext_file_dbase_init/release` bind the backend to `SEMANAGE_FILE_DTABLE`.

Control flow: parsing skips blank/comment lines, fetches the regex expression, optionally recognizes an object type token (`-d`, `--`, etc.), treats an unrecognized second token as the context, converts context text with `semanage_context_from_string`, and requires trailing whitespace/end-of-line via `parse_assert_space`. Printing uses `semanage_context_to_string` only when a context exists.

State/persistence: persistence is the read-only/read-write file pair provided to `dbase_file_init`. The parser mutates a caller-created record. Dependencies are `parse_utils`, `database_file`, fcontext record APIs, and context conversion.

Risks: parser behavior intentionally allows omitted type by falling through to context processing; malformed spacing or invalid contexts abort the record. Tests should include each file type token, omitted type, `<<none>>`, comments/blank lines, invalid context diagnostics, and round-trip print/parse.

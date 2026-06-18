# sources/sync-backup/casync/src/util.h

Purpose: declares and defines casync's common utility API, macros, cleanup helpers, endian helpers, string/path predicates, numeric helpers, and allocation helpers.

Important APIs/types/functions: exposes allocation macros `new/new0/newa`, safe `MAX/MIN`, `IN_SET`, cleanup functions, safe close/fclose helpers, little-endian read/write, `memdup`, random helpers, string macros (`streq`, `startswith`, `strjoina`, STRV helpers), path predicates, fd I/O functions, formatting constants, `GREEDY_REALLOC`, and many prototypes implemented in `util.c`.

Control flow/state: header-only macros often evaluate arguments carefully with GCC extensions. Cleanup macros integrate with automatic variable cleanup attributes.

Dependencies/integration: includes libc, Linux fs headers, `gcc-macro.h`, and `log.h`; it is the common substrate for the whole C codebase.

Risks/test signals: macro complexity can hide type and lifetime mistakes, especially stack allocation via `strjoina/newa` and ownership transfer with cleanup attributes. Broad integration tests are the main regression signal.

Source research group: `subset-b-009122`.

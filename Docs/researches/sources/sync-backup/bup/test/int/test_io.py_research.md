# sources/sync-backup/bup/test/int/test_io.py

Purpose: validates quoting/escaping helpers in `bup.io` for shell-safe bytes/strings, display of command messages, and SQL identifier/string quoting.

Important APIs/types/functions: `enc_dsq`, `enc_dsqs`, `enc_sh`, `enc_shs`, `cmd_msg`, `qsql_id`, and `qsql_str`. `_dsq_enc_byte()` is a local oracle for ANSI-C `$'...'` byte escaping.

Control flow: byte quoting loops through byte values 1..255 and string quoting loops through ASCII 1..127, testing standalone, prefix, suffix, and infix positions. Shell quoting tests distinguish empty strings, control bytes, single quotes, NUL, DEL, shell metacharacters, printable Unicode, and surrogate-escaped undecodable bytes. SQL tests assert doubled quote behavior for identifiers and string literals.

State and persistence behavior: pure functional tests with no persistent state. The only state is local in-memory byte/string construction.

Dependencies/integration points: integrates with bup's command logging and shell rendering logic, especially code paths that must safely display arbitrary bytes from filesystem paths or subprocess arguments. SQL quoting supports SQLite-facing call sites.

Risks and test signals: exhaustive byte coverage catches regressions in escaping tables. Test expectations encode bash-style ANSI-C quoting and may need review if bup deliberately changes shell dialect support. Failures are exact quoted-string mismatches.

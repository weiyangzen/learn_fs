<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c_research.md`. Source lines read for this pass: 149.

## Purpose
Debugging support for printing an `ecryptfs_auth_tok` structure and its nested password/private-key/session-key fields.

## Important APIs, Types, And Functions
Defines `PRINT`, `dump_hex`, and `dump_auth_tok`; it reads `struct ecryptfs_auth_tok`, `struct ecryptfs_password`, and eCryptfs flag constants.

## Control Flow
`dump_auth_tok` switches on token type, prints password or private-key metadata, then prints session-key flags and encrypted/decrypted key buffers when present. `dump_hex` formats bytes as dotted hex with line breaks.

## State And Persistence Behavior
No persistence, but it emits sensitive in-memory token data to stdout or syslog depending on `USE_PRINTF`.

## Dependencies And Integration Points
Depends on eCryptfs public headers and either stdio or syslog.

## Risks And Edge Cases
The file is intentionally unsafe for production diagnostics because it can print passphrases and key material. Fixed-size local formatting buffers rely on callers providing bounded sizes.

## Test Signals
Useful only in debug builds or manual token inspection; there is no automated test in this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok.c -->

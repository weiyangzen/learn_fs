<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c_research.md`. Source lines read for this pass: 49.

## Purpose
Small diagnostic entry point for dumping an auth token stored in the kernel keyring by numeric key id.

## Important APIs, Types, And Functions
Defines `main`, calls `keyctl(KEYCTL_READ, key_id, ...)`, and delegates decoded printing to `dump_auth_tok` from `dump_auth_tok.c`.

## Control Flow
Parses one key-id argument with `atoi`, reads a raw `struct ecryptfs_auth_tok` payload from that key, prints a success line, and dumps the decoded token fields.

## State And Persistence Behavior
Reads keyring state only; produces diagnostic output that can contain secret key material.

## Dependencies And Integration Points
Depends on keyutils, libecryptfs token layout, and a readable eCryptfs key id in the current keyring.

## Risks And Edge Cases
Sensitive output and keyring permission assumptions are the main risks. The `atoi` parse gives weak validation, and the include name is the legacy `keyutil.h` form.

## Test Signals
Manual test requires inserting a known auth token, passing its key id, and confirming the expected fields are decoded.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/dump_auth_tok_key.c -->

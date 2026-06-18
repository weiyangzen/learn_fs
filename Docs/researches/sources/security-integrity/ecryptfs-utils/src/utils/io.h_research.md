<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.h -->
# sources/security-integrity/ecryptfs-utils/src/utils/io.h

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/io.h_research.md`. Source lines read for this pass: 32.

## Purpose
Header declaring shared I/O/menu helpers used by eCryptfs utilities.

## Important APIs, Types, And Functions
Declares `main_menu`, `manager_menu`, `read_passphrase_salt`, `get_string_stdin`, `ecryptfs_select_key_mod`, and `mygetchar`.

## Control Flow
No execution; establishes compile-time interface between `io.c`, `mount.ecryptfs.c`, `manager.c`, and related helpers.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Includes `ecryptfs.h` for constants and struct declarations.

## Risks And Edge Cases
Prototype drift from `io.c` would break builds or cause undefined behavior in C89-style callers.

## Test Signals
Compilation of `mount.ecryptfs`, `ecryptfs-manager`, and `test` verifies this header contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.h -->

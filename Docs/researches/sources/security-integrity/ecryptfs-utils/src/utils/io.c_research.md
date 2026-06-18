<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/io.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/io.c_research.md`. Source lines read for this pass: 293.

## Purpose
Shared interactive I/O and menu helpers for mount and manager utilities.

## Important APIs, Types, And Functions
Functions include `mygetchar`, `get_string_stdin`, `get_string`, `manager_menu`, `read_passphrase_salt`, and `ecryptfs_select_key_mod`; private helpers disable/restore terminal echo.

## Control Flow
Input helpers read from stdin with CR-to-LF normalization and optional echo disabling. `read_passphrase_salt` prompts twice for a mount passphrase and zeroes the confirmation buffer. Menu helpers validate numeric choices and key-module selections.

## State And Persistence Behavior
No persisted state; temporarily changes terminal attributes and stores secrets in heap/stack buffers.

## Dependencies And Integration Points
Depends on termios, stdio, errno, mlock, libecryptfs constants, and key-module list structures.

## Risks And Edge Cases
Terminal echo must be restored on all paths; some buffers are not mlocked or securely cleared. Dynamic stdin reading doubles buffers and must preserve NUL termination.

## Test Signals
Interactive tests should cover EOF, long input, echo on/off, invalid menu selections, and passphrase mismatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/io.c -->

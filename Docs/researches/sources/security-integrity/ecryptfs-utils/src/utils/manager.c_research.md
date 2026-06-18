<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/manager.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/manager.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/manager.c_research.md`. Source lines read for this pass: 147.

## Purpose
Interactive key-management menu for adding passphrase/public-key auth tokens or invoking key generation.

## Important APIs, Types, And Functions
Main program uses `manager_menu`, `read_passphrase_salt`, `ecryptfs_validate_keyring`, `ecryptfs_add_passphrase_key_to_keyring`, key-module selection/list APIs, and `ecryptfs_generate_key`.

## Control Flow
Validates keyring integrity, loops over menu selections, adds a passphrase key after prompting, tries public-key module selection/insertion, calls key-generation helper, or exits.

## State And Persistence Behavior
Writes auth tokens to the kernel keyring; otherwise only interactive terminal state.

## Dependencies And Integration Points
Depends on keyutils, libecryptfs, io helpers, decision graph/key module structures, and libgcrypt/key module build dependencies.

## Risks And Edge Cases
Some public-key generation paths are incomplete because `gen_key.c` is stubbed. Interactive secret handling has the same terminal and memory risks as `io.c`.

## Test Signals
Manual test the menu under a working keyring; passphrase insertion can be validated with `keyctl list @u`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/manager.c -->

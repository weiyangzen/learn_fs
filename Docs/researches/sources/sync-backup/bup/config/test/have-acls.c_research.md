# sources/sync-backup/bup/config/test/have-acls.c

## Purpose
Configure-time C probe that checks for complete POSIX ACL support needed by bup.

## Important APIs, Types, and Functions
Includes `<sys/acl.h>` and `<acl/libacl.h>`, then references `acl_from_text`, `acl_get_file`, `acl_set_file`, `acl_extended_file`, and `acl_to_any_text` from `main`.

## Control Flow
The program only prints function pointer values. Successful compilation/linking proves headers and symbols are usable.

## State and Persistence Behavior
No persistent state. Its success influences generated `config/config.h` and `config/config.vars` ACL flags.

## Dependencies and Integration Points
Called by `configure` with pkg-config or `-lacl` flags. Enables `_helpers.c` ACL read/apply functions and build/link flags.

## Risks and Test Signals
Risk is false-positive support if symbols compile but runtime filesystem support is absent. The configure signal is compile/link success for all required ACL functions.

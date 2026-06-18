<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.c -->
# sources/user-network-fs/ksmbd-tools/adduser/user_admin.c

## Purpose

Implements user database mutation for `ksmbd.adduser`. It prompts for passwords, derives NT hashes, serializes users, and prevents deleting users still required by global or share configuration.

## Important APIs, Types, and Functions

Important functions include `command_add_user`, `command_update_user`, `command_delete_user`, `process_password`, `__prompt_password_stdin`, `__utf16le_convert`, `__md4_hash`, `__base64_encode`, `get_conf_contents`, and `__is_transient_user`.

## Control Flow

Add checks for duplicates, obtains a password, converts UTF-8 to UTF-16LE, MD4-hashes it, Base64-encodes the 16-byte hash, adds the user to the user manager, and rewrites pwddb. Update replaces an existing password. Delete first scans global guest and share user maps to ensure the account is transient.

## State and Persistence Behavior

Persistent state is the full `ksmbdpwd.db` file, serialized as sorted non-guest `name:hash` lines. Interactive state is raw terminal password entry with confirmation and UTF-8 validation.

## Dependencies and Integration Points

Depends on GLib, termios, config parser printable checks, tools charset/base64 helpers, MD4 implementation, management/user and share maps.

## Risks and Edge Cases

The password prompt must restore terminal echo/canonical mode. The command-line password path can leak secrets. MD4 is required for NT hash compatibility but is not a general-purpose secure hash. `get_conf_contents` rewrites the whole database.

## Test Signals

Tests should cover known NT hash vectors, prompt mismatch and invalid UTF-8, empty and max-length passwords, add/update/delete persistence, and deletion refusal for guest or share-referenced users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.c -->

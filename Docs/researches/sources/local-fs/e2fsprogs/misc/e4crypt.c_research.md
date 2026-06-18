# File Research: sources/local-fs/e2fsprogs/misc/e4crypt.c

## Purpose
Implements `e4crypt`, an ext4 encryption policy and key management utility using kernel keyrings and legacy ext4 encryption ioctls.

## Main Behaviors
- Provides subcommands:
  - `add_key`
  - `get_policy`
  - `new_session`
  - `set_policy`
  - hidden `help`
- Supports direct libc `keyctl`/`add_key` or syscall fallbacks.
- Reads salts from command-line strings, files/directories via `EXT4_IOC_GET_ENCRYPTION_PWSALT`, UUIDs, or mounted ext4 filesystems.
- Prompts for passphrase with terminal echo disabled.
- Derives raw encryption key with the file’s PBKDF2-like SHA512 routine.
- Computes key descriptor as SHA512(SHA512(key)) truncated to ext4 descriptor size.
- Inserts keys as `logon` keys with description prefix `ext4:`.
- Sets and gets encryption policy via `EXT4_IOC_SET_ENCRYPTION_POLICY` and `EXT4_IOC_GET_ENCRYPTION_POLICY`.
- Can create a new session keyring and push it to parent process with keyctl commands.

## Important Functions
- `validate_paths`: ensures path arguments are writable directories.
- `hex2byte`: parses lowercase hex descriptors.
- `parse_salt`: accepts text, hex, UUID, file, and directory salt forms.
- `clear_secrets`, `sigcatcher_setup`: clear passphrase/key material on normal/error signal paths.
- `set_policy`: builds `ext4_encryption_policy` and applies it to directories.
- `pbkdf2_sha512`: derives ext4 key material from passphrase and salt.
- `get_passphrase`: terminal echo-disabled passphrase read.
- `get_keyring_id`: maps `@us`, `@u`, `@s`, `@g`, `@p`, `@t`, or numeric keyring IDs.
- `generate_key_ref_str`: computes printable key descriptor.
- `insert_key_into_keyring`: searches then inserts a logon key.
- `get_default_salts`: scans `/etc/mtab` ext4 mounts and queries salts.
- `do_add_key`, `do_set_policy`, `do_get_policy`, `do_new_session`, `do_help`: command implementations.

## Dependencies
- Linux keyring syscalls.
- ext4 encryption ioctl structures/constants from ext2fs/ext4 headers.
- UUID parsing.
- `/etc/mtab` mount table.
- Terminal control APIs.

## Notes and Edge Cases
- Only lowercase hex descriptors are accepted by `set_policy`.
- The command uses older ext4 encryption APIs and policy version `0`.
- `add_key` with no explicit salt queries mounted ext4 filesystems for default salts.
- Signal handlers attempt to clear in-memory secrets before exit.

# File Research: sources/local-fs/e2fsprogs/misc/e4crypt.8.in

## Purpose
Manual page template for `e4crypt`, an ext4 encryption management utility.

## Documented Commands
- `e4crypt add_key [-vq] [-S salt] [-k keyring] [-p pad] [path ...]`
- `e4crypt get_policy path ...`
- `e4crypt new_session`
- `e4crypt set_policy [-p pad] policy path ...`

## Behavior Described
- `add_key` prompts for a passphrase, derives encryption keys from salts, inserts them into a keyring, and optionally applies policy to directories.
- Salt can be a text salt (`s:`), hex salt (`0x`), filename (`f:` or absolute path), or UUID.
- `pad` controls filename padding and must be one of the supported values.
- `get_policy` prints directory policy key descriptors.
- `new_session` creates a new session keyring.
- `set_policy` applies an existing 16-hex-character key descriptor to directories.

## See Also
- `keyctl`
- `mke2fs`
- `mount`

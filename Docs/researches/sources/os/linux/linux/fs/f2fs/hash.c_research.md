# File Research: sources/os/linux/linux/fs/f2fs/hash.c

Read completely: 137 lines.

## Summary
Implements F2FS filename hashing. It uses the ext3-derived TEA hash for ordinary names and casefold-aware handling for Unicode and encrypted directories.

## Main Responsibilities
- Converts byte strings into TEA hash input words.
- Computes the F2FS directory hash value.
- Handles `.` and `..` specially.
- Hashes casefolded names when casefolding is enabled.
- Uses fscrypt SipHash for encrypted casefolded plaintext names.

## Key APIs
- `f2fs_hash_filename()`.
- Internal helpers: `TEA_transform()`, `str2hashbuf()`, `TEA_hash_name()`.

## Important Behavior
The TEA hash initializes with fixed ext-style seed values, processes names in 16-byte chunks, and masks out `F2FS_HASH_COL_BIT`.

For casefolded directories, the function prefers the precomputed Unicode casefolded name. If the name is invalid Unicode or otherwise lacks `cf_name`, it hashes the user-supplied plaintext name as opaque bytes. For encrypted casefolded directories, it hashes plaintext through `fscrypt_fname_siphash()` instead of hashing ciphertext.

`name_is_dot_dotdot()` returns hash zero for `.` and `..`.

## Risks
Directory lookup correctness depends on hashing the same logical name representation that insertion used. Casefolded encrypted directories are especially sensitive: falling back to `usr_fname` rather than `disk_name` is required so ciphertext does not determine casefold lookup hashes.

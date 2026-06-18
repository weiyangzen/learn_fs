# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.8.in

## Role

Manual page for `ntfsdecrypt`, a tool for decrypting or updating NTFS EFS-encrypted files from an unmounted NTFS volume.

## Documented Interface

Documents keyfile selection with `--keyfile`, inode or path target selection, `--encrypt` update mode, force, quiet/verbose, version, and help.

## Important Behavior

Explains the two-level EFS scheme: file data is encrypted by a symmetric FEK, and the FEK is encrypted for authorized users/recovery agents in `$LOGGED_UTILITY_STREAM` / `$EFS`. It documents supported symmetric modes as DESX, 3DES, and AES-256.

## Research Notes

The page highlights that encrypted-file backups must include `$LOGGED_UTILITY_STREAM`; otherwise decryption is impossible even with a recovery key.

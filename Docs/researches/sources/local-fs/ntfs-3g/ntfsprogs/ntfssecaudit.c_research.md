# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfssecaudit.c

## File Role

`ntfssecaudit.c` implements `ntfssecaudit`, a standalone NTFS security metadata inspection, backup, restore, audit, and permission-setting utility. It works through libntfs-3g security APIs and can operate on unmounted NTFS volumes as root, mounted NTFS files via extended attributes on Unix builds with xattr support, and Windows paths with drive/path splitting support.

The program covers several distinct command families:

- audit raw `$Secure` metadata: `$SDS`, `$SII`, and `$SDH`
- display security descriptors from raw hex dumps
- display NTFS ACL/security information for a file or recursive tree
- back up ACLs and Windows file attributes in a textual/hex dump format
- restore ACL backups, optionally including Windows attributes
- set file permissions from an octal mode or POSIX ACL description
- generate `.NTFS-3G/UserMapping` proposals from file owner/group SIDs
- optional compile-time self-tests for SID, mode, and POSIX ACL conversions

## Major Dependencies

The file uses ntfs-3g internals heavily:

- `security.h` and `acls.h` for security descriptor parsing, SID mapping, permission conversion, and file security APIs
- `volume.h`, `inode.h`, `attrib.h`, `index.h`, `mft.h`, `layout.h`, `mst.h`, and `runlist.h` for raw NTFS metadata access
- `unistr.h`, `ntfstime.h`, `endians.h`, `types.h`, and `utils.h` for encoding, timestamps, endian-safe fields, and support routines
- `realpath.h` and OS headers for mounted-file and mapping-file path handling
- optional `sys/xattr.h` for mounted Unix file ACL display through `system.ntfs_acl` and `system.ntfs_attrib`

The build entry in `ntfsprogs/Makefile.am` lists `ntfssecaudit.c` with `utils.c` and links it against the normal ntfs-3g libraries plus `NTFSRECOVER_LIBS`.

## Core State

Important file-global state:

- `cmd`: selected command mode (`CMD_AUDIT`, `CMD_BACKUP`, `CMD_HEX`, `CMD_SET`, `CMD_USERMAP`, etc.)
- `opt_e`, `opt_r`, `opt_u`, `opt_v`: restore-extra, recurse, user-map proposal, and verbosity controls
- `errors`, `warnings`: accumulated severe and non-severe diagnostics, which drive exit status
- `ntfs_context`: active `SECURITY_API` returned by `ntfs_initialize_file_security`
- `context.mapping` and `mappingtype`: local/external/dummy SID-to-uid/gid mapping state
- `securdata[]`: sparse block table indexed by NTFS security ID, used to correlate `$SDS`, `$SII`, `$SDH`, recursive file usage counts, descriptor hashes, offsets, lengths, and display deduplication

Key structs local to this file include `SII` and `SDH` on-disk index-entry images, `SECURITY_DATA` for cross-checking security IDs, and small linked-list/callback structs used when recursively enumerating directories.

## Security Descriptor Display

The low-level helpers read and write little-endian fields from raw descriptor bytes (`get2l`, `get4l`, `get6h`, `get8l`, `set2l`, `set4l`), compute NTFS security hashes, and produce hex dumps.

Descriptor presentation is layered:

- `showsid()` decodes and labels well-known SIDs where possible, then prints hex and decimal SID forms.
- `showheader()` prints descriptor revision, control flags, and owner/group/SACL/DACL offsets.
- `showace()` decodes ACE type, inheritance/audit flags, access masks, standard rights, generic rights, SID, and a compact grant/deny summary.
- `showacl()`, `showdacl()`, and `showsacl()` walk ACLs and ACEs.
- `showownership()` prints Windows owner/group SIDs and optional account names on Windows.
- `linux_permissions()` and, when compiled with POSIX ACL support, `linux_permissions_posix()` derive Unix mode or POSIX ACL views from the NTFS descriptor.

`showhex()` reads text containing hex dump lines, reconstructs descriptors, validates them with `ntfs_valid_descr`, computes hashes, estimates file-vs-directory from inheritable ACEs, and displays the descriptor at high verbosity.

## Mapping Handling

`local_build_mapping()` searches for `.NTFS-3G/UserMapping` near a mounted file path on Unix or in the NTFS root on Windows. If no mapping is found, it installs a default single-user mapping using the default security authority constants. This mapping feeds Unix owner/group interpretation and POSIX ACL conversion.

`proposal()` generates a candidate UserMapping snippet when a file owner and group look like Windows domain SIDs (`S-1-5-21-...`). On Unix it tries to locate the NTFS filesystem root by walking toward inode 5 and prints an example `.NTFS-3G/UserMapping` path.

## Backup and Restore

`showfull()` is the central display/backup routine. It gathers owner, group, DACL, SACL, and Windows attributes separately, merges descriptor parts into a single self-relative descriptor, validates it, computes hashes, displays or stores security-key data, and prints interpreted Unix ownership/mode.

`backup()` opens an unmounted volume read-only and recursively calls `recurseshow()` from a root path, producing a textual ACL collection with security-key summaries.

`restore()` parses a backup stream. It detects file/directory markers, security keys, Windows attribute lines, descriptor hex dumps, and expected hashes. `applyattr()` then reuses explicit descriptors or previously stored descriptors by key, optionally restores Windows attributes, and calls `ntfs_set_file_security()` with owner, group, DACL, and SACL selection flags.

`dorestore()` requires root, opens the volume read-write, runs `restore()`, and closes the security API.

## Permission Setting

For non-POSIX-ACL builds, `setfull()` reads the current descriptor, extracts current owner/group SIDs, builds a new descriptor from an octal mode with `ntfs_build_descr()`, and writes owner/group/DACL information back.

For POSIX ACL builds, `encode_posix_acl()` parses strings like `[d:]{u,g,m,o}:id:perms,...` or octal modes into a `POSIX_SECURITY` object, including implicit mask insertion. `setfull_posix()` merges requested ACL/mode changes with the old POSIX descriptor, builds a new NTFS descriptor through `ntfs_build_descr_posix()`, and writes it back.

Recursive setting uses `recurseset()` or `recurseset_posix()` and directory enumeration via `ntfs_read_directory()` plus `callback()`.

## Mounted-File Path

On Unix with xattr support, `processmounted()` handles display or mapping proposal for already mounted NTFS files without root/unmounted-volume access. It reads:

- `system.ntfs_acl` for the raw NTFS security descriptor
- `system.ntfs_attrib` for Windows attributes

It then validates and displays the descriptor using the same conversion/display helpers. Without xattr support, this mode reports that an unmounted partition must be used.

## Raw `$Secure` Audit

The audit mode validates consistency across NTFS security metadata:

- `audit_sds(FALSE)` and `audit_sds(TRUE)` read the two `$SDS` copies, validate descriptor entry sizes, hashes, offsets, security IDs, ordering, and deleted entries.
- `audit_sii()` walks `$SII` index entries sorted by security ID and cross-checks hash, offset, and length against `$SDS`.
- `audit_sdh()` walks `$SDH` index entries sorted by hash/security ID and cross-checks the same metadata.
- `audit_summary()` reports security IDs not present in every expected structure and, with recursion, file-use counts.

`SECURITY_DATA.flags` records whether each ID was seen in `$SDS-1`, `$SDS-2`, `$SII`, and `$SDH`.

## CLI and Control Flow

`parse_options()` accepts `-a`, `-b`, `-e`, `-h`, `-H`, `-r`, `-s`, `-u`, `-v`, `-V`, and compile-time `-t`. It rejects incompatible commands and returns the index of the first non-option argument.

`main()` prints a banner, initializes global tables and mappings, dispatches command-specific argument shapes, reports warnings/errors to stdout and stderr when stdout is redirected, frees split Windows paths and security blocks, and exits nonzero when command syntax failed or severe errors were recorded.

## Notable Risks and Maintenance Notes

- The file is large and multiplexes raw-volume, mounted-file, Windows-path, backup/restore, and POSIX ACL behaviors through global state.
- Several descriptor parsers assume bounded raw byte layouts and depend on `MAXATTRSZ` and `ntfs_valid_descr()` to reject malformed descriptors.
- Restore mode applies descriptors from text backup streams and trusts security-key reuse after hash checks.
- Root/write operations are guarded by `getuid()` and open mode, but permission-setting and restore paths directly modify NTFS security metadata.
- The optional self-test code is extensive but disabled by `SELFTESTS 0` in this file.

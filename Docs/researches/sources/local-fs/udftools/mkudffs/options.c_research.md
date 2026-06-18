# File Research: sources/local-fs/udftools/mkudffs/options.c

## Role

Command-line option parser and media-policy configurator for `mkudffs`.

## Main Responsibilities

- Defines long options and usage text for formatting controls.
- Parses block size, UDF revision, labels/identifiers, ownership strings, UID/GID/mode, boot area policy, allocation strategy, sparing/VAT controls, media type, space accounting, allocation descriptor type, charset, and start/min-block controls.
- Mutates `struct udf_disc` and global default descriptor templates while parsing.
- Auto-detects optical media profile when `--media-type` is omitted.
- Applies media-derived defaults for partition access type, VAT/sparing use, strategy 4096, minimum CD-R track size, and BD-R revision.
- Validates incompatible option combinations before returning final media type.

## Important Functions

- `usage()` prints complete CLI help and exits.
- `parse_args()` performs all parsing, validation, media detection, partition-map setup, and sizing default selection.

## Notable Parsing Details

- `--blocksize` must be a power of two from 512 through 32768 and updates the LVD logical block size.
- `--udfrev` accepts dotted hex-like revisions such as `2.01` or raw hex input; unsupported revisions fail.
- Charset options `--locale`, `--u8`, `--u16`, and `--utf8` must be first argument because string options are encoded as they are parsed.
- `--label` is a synonym for both LVID and VID; if VID is too short for a long label, it stores a truncated version unless the user explicitly used `--vid`.
- `--uuid` must be exactly 16 lowercase hex characters.
- `--vsid` preserves or converts the UUID prefix portion of the Volume Set Identifier depending on 8-bit or 16-bit OSTA dstring form.
- `--media-type` must be supplied before `--udfrev` because media can set the default UDF revision.
- `--spartable` and `--vat` are mutually exclusive.
- `--minblocks` and `--closed` are valid only with VAT/write-once media.
- UDF >= 2.50 is rejected for non-VAT disks because metadata partition creation is not implemented.

## Media Policy

- HD and DVD-RAM map to overwritable access.
- DVD/CD read-only profiles map to read-only access.
- DVD-R, CD-R, and BD-R enable VAT and write-once access.
- DVD-RW and CD-RW enable sparable partitions.
- WORM and MO default to strategy 4096 and blank terminal behavior.
- BD-R defaults to UDF 2.50 if the revision was not explicitly supplied.

## Dependencies

- `mkudffs.h` for media constants and partition map helpers.
- `defaults.h` for default descriptor templates and sizing profiles.
- Linux CD-ROM ioctls for media autodetection.

## Research Notes

This file is policy-heavy. Formatter behavior often depends on parse order: charset options must come before strings, sparing options must precede sparing-space options, and media type must precede explicit revision.

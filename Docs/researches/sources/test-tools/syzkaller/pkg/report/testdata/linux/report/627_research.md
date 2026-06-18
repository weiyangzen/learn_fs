# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/627

## Purpose
This fixture covers a panicking KASAN slab-out-of-bounds read attributed to `ext4_group_desc_csum`.

## Important APIs, types, and functions
Key symbols include `crc16`, `ext4_group_desc_csum`, ext4 metadata validation paths, KASAN allocation evidence, and `panic_on_warn`.

## Control flow
An ext4 operation computes or verifies a group descriptor checksum, `crc16` reads beyond a slab object, KASAN reports the invalid access, and panic-on-warn converts it into a panic.

## State and persistence behavior
The file stores KASAN object bounds, allocation stack, memory state, and `PANICKED: Y`.

## Dependencies and integration points
It integrates KASAN slab-out-of-bounds parsing with ext4 filesystem symbol attribution and panic handling.

## Risks and test signals
The parser must not title the report as `crc16`; the expected title is `KASAN: slab-out-of-bounds Read in ext4_group_desc_csum`.

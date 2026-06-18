# File Research: sources/os/linux/linux-stable/fs/hpfs/hpfs.h

## Purpose

Defines HPFS on-disk structures, constants, endian-dependent bitfields, and low-level accessors.

## Main Contents

Defines sector-number typedefs, boot block, super block, spare block, code-page structures, dnodes and dirents, B+ tree headers and nodes, fnodes, anodes, and extended attributes. It also defines magic values, B+ tree flags, fnode flags, EA flags, and helpers such as `bp_internal()`, `bp_fnode_parent()`, `fnode_in_anode()`, `fnode_is_dir()`, `ea_indirect()`, and `ea_in_anode()`.

## Dependencies

Requires the build endian macros and Linux flexible-array/container helpers. The structures are consumed by every HPFS source file.

## Risks

The header documents that HPFS knowledge is partly conjectural. Bitfield layouts are endian-sensitive. Any structure packing, offset, or flag change directly affects on-disk compatibility and corruption risk.

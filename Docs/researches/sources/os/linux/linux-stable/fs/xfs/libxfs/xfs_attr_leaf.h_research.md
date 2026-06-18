# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose

`xfs_attr_leaf.h` declares the in-core attr leaf header and all shortform/leaf helper APIs implemented by `xfs_attr_leaf.c`. It is the interface between the high-level attr state machine, da btree code, and leaf block implementation.

## Main Definition

`struct xfs_attr3_icleaf_hdr` is the normalized in-core header used for both legacy and CRC-enabled attr leaf blocks. It stores sibling links, magic, entry count, used bytes, 32-bit `firstused`, hole indicator, and the three freemap regions. The widened `firstused` avoids overflow for 64 KiB attr blocks; disk conversion handles the narrower on-disk fields.

## Declared APIs

The header groups declarations by role:

- shortform operations: create, replace, add, getvalue, convert to leaf, remove, find, allfit, bytesfit, verify, and fork removal;
- one-block leaf operations: convert to node, convert to shortform, clear/set/flip INCOMPLETE flags;
- growing helpers: split, lookup, getvalue, add, remove, list;
- shrinking helpers: leaf init, toosmall, unbalance;
- utility helpers: last hash, leaf ordering, new entry size, read, header conversion, and header check.

## Integration Notes

High-level callers use this header to avoid knowing whether an attr fork is shortform, single leaf, or part of a da btree. The header also exposes verifier/conversion helpers needed by repair, btree code, and transaction code.

## Invariants

Callers rely on `xfs_attr3_icleaf_hdr` representing disk state faithfully after endian conversion. APIs that take `struct xfs_da_args` expect `args->geo`, `args->trans`, `args->dp`, `args->owner`, and `args->whichfork` to be populated consistently.

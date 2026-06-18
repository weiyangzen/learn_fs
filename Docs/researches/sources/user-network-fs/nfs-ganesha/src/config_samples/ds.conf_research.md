# sources/user-network-fs/nfs-ganesha/src/config_samples/ds.conf

## Purpose

`ds.conf` is a minimal Data Server configuration sample for pNFS/DS-style setups.

## Important APIs, Types, and Functions

It defines a `DS` block with optional `Number` and nested `FSAL` block setting `Name = GPFS`.

## Control Flow

The parser reads one top-level `DS` block. Semantic loading should assign DS number 0 and associate the DS with the GPFS FSAL.

## State and Persistence Behavior

The file itself persists no runtime state; it configures a server role and FSAL binding. DS identity uniqueness matters when multiple DS instances are deployed.

## Dependencies and Integration Points

It integrates with GPFS FSAL and any Ganesha pNFS data-server configuration loader.

## Risks and Edge Cases

It is intentionally minimal and omits access/export details, so it is not a full operational config. Duplicate DS numbers in a larger deployment would be a semantic risk.

## Test Signals

Parser syntax validation and DS block loader tests should accept this sample and apply the default number. GPFS-enabled builds are needed for runtime validation.

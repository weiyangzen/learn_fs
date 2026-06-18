# sources/distributed-fs/tahoe-lafs/src/allmydata/test/strategies.py

## Purpose
This file centralizes Hypothesis strategies for Tahoe-LAFS tests. It builds random but structurally valid write capabilities, write keys, fingerprints, offsets, lengths, and base32 text.

## Important APIs, Types, And Functions
Public strategy functions include `write_capabilities`, `ssk_capabilities`, `ssk_writekeys`, `ssk_fingerprints`, `mdmf_capabilities`, `mdmf_writekeys`, `mdmf_fingerprints`, `dir2_capabilities`, `dir2_mdmf_capabilities`, `offsets`, `lengths`, and `base32text`. Private helpers `_writekeys` and `_fingerprints` create fixed-size byte strategies. Capability constructors come from `allmydata.uri`.

## Control Flow
The strategies are declarative. `write_capabilities` composes SSK file, MDMF file, SDMF directory, and MDMF directory strategies with `one_of`; each capability strategy uses `builds` to call the real URI constructor with generated key and fingerprint bytes.

## State, Persistence, And Dependencies
There is no mutable state or persistence. Dependencies are Hypothesis and Tahoe URI/base32 modules.

## Risks And Test Signals
These strategies are used by property tests such as `NodeMakerTests` and therefore define what cap variants those tests cover. They generate syntactically valid objects but do not constrain semantic compatibility beyond constructor requirements, so tests using them still need explicit assumptions for invalid combinations like mutable caps with deep immutable nodes.

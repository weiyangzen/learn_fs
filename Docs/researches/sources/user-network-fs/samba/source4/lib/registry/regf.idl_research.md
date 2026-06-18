# sources/user-network-fs/samba/source4/lib/registry/regf.idl

## Purpose

`regf.idl` defines the TDR-serializable structures for the Windows REGF registry hive format used by `regf.c`. It is the schema source for generated parsers and pushers for REGF headers, HBIN containers, key records, value records, security records, and subkey-list records.

## Important APIs, Types, and Functions

The IDL exports `regf_hdr`, `hbin_block`, `nk_block`, `sk_block`, `lh_block`, `li_block`, `ri_block`, `vk_block`, and `lf_block`. It also defines `regf_version`, `reg_key_type`, `lh_hash`, and `hash_record`, plus `REGF_OFFSET_NONE`. Generated functions such as `tdr_pull_regf_hdr()`, `tdr_push_hbin_block()`, and `tdr_pull_nk_block()` are consumed by `regf.c`.

## Control Flow

There is no runtime control flow in the IDL itself. At build time `wscript_build` runs `SAMBA_PIDL('PIDL_REG', source='regf.idl', options='--header --tdr-parser')`, producing C definitions and TDR functions. At runtime `regf.c` uses those generated routines to parse cells returned by `hbin_get()` and to serialize changed blocks into HBIN storage or the output file descriptor.

## State and Persistence Behavior

The schema captures persisted REGF state: header update counters, modification time, version, root data offset, HBIN sizes, signed cell lengths, key metadata, value metadata, and circular security descriptor lists. Variable-length arrays are tied to count or length fields, so mismatches between record counts and actual cell sizes become parser and corruption risks.

## Dependencies and Integration Points

The IDL depends on Samba PIDL/TDR conventions, NTTIME, DOS and UTF16 charset annotations, and generated C support. It integrates directly with `TDR_REGF` and the private `registry` library. REGF tests indirectly verify the generated types by creating and reading hives.

## Risks and Edge Cases

The schema documents partially understood fields (`uk*`, `unknown_offset`, `unk3`) and assumes DOS-encoded key/value names. `vk_block.data_length` uses its top bit to indicate inline data, so consumers must mask it correctly. REGF minor-version differences determine whether subkey lists are LI, LF, or LH, and the schema also allows RI indirection that write support does not fully implement.

## Test Signals

Build success of `PIDL_REG` and `TDR_REGF` is the primary compile signal. Runtime signals come from opening real REGF hives, creating Samba REGF hives, round-tripping key/value/security changes, and parsing all list record kinds (`li`, `lf`, `lh`, and `ri`).

Source-read signal: reviewed complete local file (167 lines).

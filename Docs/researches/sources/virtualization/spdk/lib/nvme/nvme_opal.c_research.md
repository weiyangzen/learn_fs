# File Research: sources/virtualization/spdk/lib/nvme/nvme_opal.c

## Purpose

Implements SPDK NVMe Opal support for TCG storage security over NVMe Security Send/Receive. It constructs and parses Opal tokens, runs synchronous session-style command flows on the NVMe admin queue, discovers Opal capabilities, and exposes public `spdk_opal_*` commands for ownership, Locking SP activation, locking range setup/status, user/password management, revert, erase, and secure erase.

## Main Responsibilities

- Wrap NVMe Security Send/Receive into `opal_send_recv()`, using async admin commands internally and polling admin completions until a session callback marks completion.
- Serialize Opal commands into a fixed `IO_BUFFER_LENGTH` command buffer with tiny/short/medium atom helpers, byte-string insertion, numeric tokens, and final packet/subpacket length fixups.
- Parse Opal responses into `spdk_opal_resp_parsed`, classifying tiny/short/medium/long atoms and token atoms, then extract method status, unsigned integers, and byte strings.
- Run Discovery0, validate supported security protocols, parse feature descriptors, and populate `spdk_opal_dev` feature/comid state.
- Manage Opal sessions with host/session numbers, authentication UIDs, and TCG methods.
- Implement high-level command workflows: take ownership, construct/destruct device, revert TPer, activate Locking SP, lock/unlock range, setup range, query max ranges/range info, enable/add users, set passwords, erase, and secure erase by regenerating active key.

## Key Control Flow

Construction starts in `spdk_opal_dev_construct()`: allocate device and payload, run `opal_discovery0()`, parse Discovery0 features in `opal_discovery0_end()`, and store the selected comid. Most public commands allocate an `opal_session`, initialize a key with `opal_init_key()`, start either a generic SP session or authenticated Locking SP session, perform one or more command builders, call `opal_send_recv()`, parse method status, then call `opal_end_session()`.

`spdk_opal_cmd_take_ownership()` is a multi-session flow: open Admin SP as Anybody, read MSID PIN, end session, reopen as SID using MSID, then set the SID C_PIN to the new password.

## State and Data

Primary mutable state is `struct spdk_opal_dev` from `nvme_opal_internal.h`: controller pointer, comid, Discovery0 feature info, cached max ranges, and per-locking-range info. Per-command state lives in `struct opal_session`: command/response buffers, parsed response tokens, session IDs, completion callback fields, and synchronous completion status.

## Integration Points

Depends on NVMe controller admin command APIs for security send/receive and completion polling. Uses Opal constants and wire structs from `spdk/opal_spec.h`, public types from `spdk/opal.h`, and SCSI security protocol values from `spdk/scsi_spec.h`.

## Risk Notes

- The parser stores up to `MAX_TOKS` response tokens but does not visibly guard `num_entries` against exceeding that array while parsing malformed large responses.
- `opal_add_token_u64()` writes directly to the command buffer without the same explicit buffer-bound checks used by byte-string helpers.
- Several public wrappers combine operation and end-session return values with `ret += opal_end_session(...)`, which can obscure the original error code.
- Sensitive key material is sometimes zeroed, but not consistently for all stack/session buffers.

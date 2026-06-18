# sources/user-network-fs/samba/source3/rpcclient/cmd_spotlight.c

Purpose: this module adds MDSSVC Spotlight test commands to `rpcclient`: `fetch_properties` and `fetch_attributes`.

Important APIs, types, and functions: it uses generated `dcerpc_mdssvc_open`, `dcerpc_mdssvc_unknown1`, and `dcerpc_mdssvc_cmd`, plus Samba Spotlight helpers `dalloc_new`, `dalloc_add`, `dalloc_stradd`, `sl_pack_alloc`, `sl_unpack`, and `dalloc_dump`. It constructs `struct mdssvc_blob`, `policy_handle`, `sl_array_t`, and `sl_cnids_t`.

Control flow: both commands validate positional arguments, open an MDSSVC share context, call `unknown1` with local uid/gid, allocate a DALLOC request tree, pack it into a Spotlight blob, send `mdssvc_cmd`, unpack the response, and dump decoded content. `fetch_attributes` parses a CNID with `smb_strtoull`, requests `kMDItemPath`, and rejects empty responses.

State and persistence: local allocations are talloc/DALLOC scoped to the command. Remote state is a short-lived MDSSVC context handle; no persistent local state is written.

Dependencies and integration: depends on generated MDSSVC NDR, server-side mdssvc marshalling/dalloc headers, and `smb_strtox`. Registered in `spotlight_commands[]` and compiled into `rpcclient` by `wscript_build`.

Risks: several protocol constants are hard-coded and partly labeled unknown. The command is mostly diagnostic, so server behavior changes can break it without obvious compile failures. Large or malformed Spotlight blobs stress marshalling and dump output.

Test signals: validate usage messages, CNID parse failures, empty response handling, successful decode against an MDSSVC-enabled share, and memory-failure paths through allocation checks.

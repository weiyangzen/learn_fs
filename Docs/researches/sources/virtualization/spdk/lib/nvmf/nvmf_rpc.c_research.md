# File Research: sources/virtualization/spdk/lib/nvmf/nvmf_rpc.c

## Purpose

`nvmf_rpc.c` implements SPDK JSON-RPC handlers for configuring and inspecting the NVMe-oF target. It translates JSON parameters into internal NVMf target operations: target/transport creation, subsystem lifecycle, listener management, discovery referrals, namespace management, host access control, authentication keys, stats, controller/qpair/listener introspection, and mDNS PRR operations.

## Registered RPC Surface

The file registers these RPCs:

- Subsystems: `nvmf_get_subsystems`, `nvmf_create_subsystem`, `nvmf_delete_subsystem`.
- Listeners and ANA: `nvmf_subsystem_add_listener`, `nvmf_subsystem_remove_listener`, `nvmf_subsystem_listener_set_ana_state`, `nvmf_subsystem_get_listeners`.
- Discovery referrals: `nvmf_discovery_add_referral`, `nvmf_discovery_remove_referral`, `nvmf_discovery_get_referrals`.
- Namespaces: `nvmf_subsystem_add_ns`, `nvmf_subsystem_set_ns_ana_group`, `nvmf_subsystem_remove_ns`, `nvmf_ns_add_host`, `nvmf_ns_remove_host`.
- Host access and keys: `nvmf_subsystem_add_host`, `nvmf_subsystem_remove_host`, `nvmf_subsystem_set_keys`, `nvmf_subsystem_allow_any_host`.
- Targets: private `nvmf_create_target`, `nvmf_delete_target`, `nvmf_get_targets`.
- Transports/stats: `nvmf_create_transport`, `nvmf_get_transports`, `nvmf_get_stats`.
- Runtime inspection: `nvmf_subsystem_get_controllers`, `nvmf_subsystem_get_qpairs`.
- mDNS PRR: `nvmf_publish_mdns_prr`, `nvmf_stop_mdns_prr`.

## Main Helpers And Patterns

`_rpc_nvmf_get_subsystem()` centralizes target and optional subsystem lookup, returning JSON-RPC errors for missing default targets, named targets, or subsystem NQNs. `_rpc_nvmf_subsystem_pause()` wraps lookup plus `spdk_nvmf_subsystem_pause()` and is used by RPCs that mutate active subsystem state.

`rpc_listen_address_to_trid()` converts RPC listen-address fields into `spdk_nvme_transport_id`, including transport type parsing, optional address family parsing, IPv4 defaulting for TCP/RDMA compatibility, and fixed-size `traddr`/`trsvcid` bounds checks.

`decode_hex_string_be()` validates and decodes fixed-size hex strings for NGUID/EUI64 namespace options. Dump helpers serialize subsystems, referrals, controllers, qpairs, listeners, ANA states, and transport options into JSON.

## Control Flow

Most mutating subsystem RPCs allocate a context, decode JSON, look up the subsystem, pause it, perform the mutation in a pause callback, then resume and send the final response from the resume callback. This pattern is used for listener add/remove, listener ANA state updates, namespace add/remove, namespace ANA group changes, and namespace host visibility changes.

Subsystem creation initializes `spdk_nvmf_subsystem_opts`, overlays RPC fields through the `NVMF_CREATE_SUBSYSTEM_OPTS_FIELDS` macro, validates serial/model strings, creates the subsystem, applies host policy and controller ID range, starts it asynchronously, and destroys it on start failure.

Subsystem deletion stops the subsystem for destroy, removes listeners, destroys asynchronously when required, and reports state-change errors such as already-destroying or busy.

Transport creation is two-phase. It first decodes enough to determine `trtype`, initializes transport defaults via `spdk_nvmf_transport_opts_init()`, overlays decoded values, rejects duplicate transports, passes transport-specific JSON through `opts.transport_specific`, creates the transport asynchronously, and adds it to the target. On add failure it destroys the transport before returning the error.

Stats and qpair introspection iterate SPDK I/O channels. `nvmf_get_stats` emits target tick rate and each poll group's stats. `nvmf_subsystem_get_qpairs` pauses the subsystem, walks poll-group qpair lists across channels, dumps matching qpairs, then resumes.

## Data And Compatibility Notes

The file uses generated RPC context structs and free helpers from `spdk_internal/rpc_autogen.h`. Several TODOs indicate older hand-written extension structs remain until they can be replaced by generated RPC contexts. Static assertions guard ABI-sensitive assumptions, including subsystem options size and listener option alignment.

Deprecation logs are registered for namespace `hide_metadata` and transport fields `num_shared_buffers`, `buf_cache_size`, and `io_unit_size`. `max_io_qpairs_per_ctrlr` is decoded by adding one admin qpair to preserve the internal meaning of `max_qpairs_per_ctrlr`.

## Dependencies

This file depends on SPDK JSON-RPC, bdev, env/ticks, NVMe/NVMf APIs, string/hexlify/util/bit-array/config helpers, internal assert/RPC autogen headers, and `nvmf_internal.h`. It calls into subsystem, target, transport, namespace, listener, referral, keyring, auth dump, mDNS PRR, and poll-group statistics APIs declared elsewhere.

## Risks And Edge Cases

Important risks are asynchronous request lifetime, resume-after-error behavior, and partial mutation rollback. Listener add failure stops the just-created listener; namespace add failure during resume attempts to remove the namespace and resume again. Several introspection paths log resume failure after already sending the RPC result, with comments noting the RPC should ideally fail if resume fails. Secure-channel listener creation is rejected when `allow_any_host` is enabled. Host/key RPCs must release keyring references on every exit path. Transport option decoding happens twice, so new fields must be added consistently to the decoder, extension struct, default copy, and opts assignment blocks.

## Test/Validation Signals

Validation should include JSON decode failures, missing target/subsystem paths, subsystem create/delete success and failure, controller ID range validation, listener add/remove with transport-specific options, secure-channel plus `allow_any_host` rejection, discovery referral service ID validation, namespace add with valid/invalid NGUID/EUI64/UUID and rollback on resume failure, namespace remove and ANA group updates, host add/remove and disconnect timeout handling, DH-HMAC-CHAP key lookup failures, duplicate transport rejection, async transport create/add failure cleanup, stats over multiple poll groups, qpair/controller/listener dumps, and mDNS PRR publish/stop error propagation.

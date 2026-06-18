# sources/security-integrity/selinux/libsepol/src/node_record.c

## Purpose
Implements the high-level `sepol_node_t` and `sepol_node_key_t` record API for SELinux network node contexts. It owns conversion between textual IPv4/IPv6 addresses, binary address/mask bytes, protocol values, and attached `sepol_context_t` records.

## Important APIs, Types, and Functions
Defines private structs `sepol_node` and `sepol_node_key`, each carrying allocated address bytes, mask bytes, byte sizes, and protocol; nodes also own a cloned context. Key APIs include `sepol_node_key_create`, `sepol_node_key_extract`, `sepol_node_key_unpack`, `sepol_node_key_free`, `sepol_node_compare`, `sepol_node_compare2`, address/mask getters and setters in string and byte form, `sepol_node_get_proto`, `sepol_node_set_proto`, `sepol_node_get_proto_str`, `sepol_node_create`, `sepol_node_clone`, `sepol_node_free`, `sepol_node_get_con`, and `sepol_node_set_con`.

## Control Flow
String address creation routes through `node_alloc_addr()` for protocol-sized buffers, then `node_parse_addr()` with `inet_pton`. String getters allocate protocol-sized text buffers and call `node_expand_addr()` with `inet_ntop`. Byte setters/getters clone caller-provided buffers without validating protocol length. Clone/create/free paths consistently allocate deep copies and release owned context/address/mask memory.

## State and Persistence Behavior
All state is heap-owned by the record or key. Setters replace old address/mask/context only after allocating and parsing/cloning replacements. No policydb persistence occurs here; persistence happens when `nodes.c` converts records into `ocontext_t` lists.

## Dependencies and Integration Points
Uses `context_internal.h`/public context APIs for context cloning and freeing, `debug.h` for handle-scoped errors, libc allocation, and `inet_pton`/`inet_ntop` for canonical network conversion. The API feeds `nodes.c` policydb operations and callers of the public libsepol node-record interface.

## Risks and Edge Cases
Byte setters accept arbitrary sizes, so malformed callers can create records whose byte length does not match `proto`; later policydb conversion assumes 4 or 16 bytes. `sepol_node_compare*()` orders by mask comparison before address comparison when sizes match, which may be surprising if callers expect address-first ordering. Protocol setters do not resize existing address/mask buffers. Error messages call `sepol_node_get_proto_str()` and may show `???` for invalid protocols.

## Test Signals
Tests should cover IPv4/IPv6 parse/expand round trips, invalid address/protocol errors, deep clone independence, key extraction and comparison behavior, byte setter misuse, context ownership replacement, and cleanup under allocation failures.

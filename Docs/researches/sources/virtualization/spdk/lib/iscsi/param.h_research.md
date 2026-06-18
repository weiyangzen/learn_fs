# File Research: sources/virtualization/spdk/lib/iscsi/param.h

Full-file read: 58 lines.

This header declares the iSCSI text parameter model and negotiation API.

Main contents:
- `enum iscsi_param_type` covers invalid, unspecified, list, numerical min/max/declarative, declarative, boolean OR, and boolean AND parameter semantics.
- `struct iscsi_param` is a singly-linked node with key, value, valid-list string, type, and negotiation state index.
- Declares parse, lookup, mutation, negotiation, copy-to-runtime, and default initialization functions.

Integration points:
- Included by login/text processing and `param.c`.
- Forward-declares `struct spdk_iscsi_conn` to avoid exposing connection internals.

Risks and review notes:
- The API exposes mutable linked-list nodes and string pointers; callers must respect ownership rules from `param.c`.
- `state_index` couples runtime arrays in connection/session objects to the static parameter tables.

Testing focus:
- Compile-time coverage through consumers.
- ABI/API stability if parameter tables are extended.

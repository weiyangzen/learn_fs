<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.h -->
# sources/user-network-fs/cifs-utils/asn1.h

## Purpose

`asn1.h` declares the minimal ASN.1/BER writer interface and tag constants used inside cifs-utils.

## Important APIs, Types, and Functions

The header defines `struct nesting`, `struct asn1_data`, `ASN1_DATA`, tag construction macros such as `ASN1_APPLICATION`, `ASN1_SEQUENCE`, `ASN1_CONTEXT`, and constants for common ASN.1 types including OID, integer, boolean, octet string, bit string, enumerated, set, and general string. It declares the writer and OID encoding functions implemented in `asn1.c`.

## Control Flow

The API is stack-shaped: allocate with `asn1_init`, open nested fields with `asn1_push_tag`, write bytes or helper primitives, close nested fields with `asn1_pop_tag`, then free with `asn1_free`. Callers must check boolean returns or `has_error`.

## State and Persistence Behavior

The structures store only transient encoder state. The nested-tag linked list is owned by the `ASN1_DATA` talloc context.

## Dependencies and Integration Points

Consumers must include talloc-visible types and C integer/bool definitions before or around this header. The main in-tree consumer in this work item is `cldap_ping.c`; `data_blob.h` is used for OID output.

## Risks and Edge Cases

The structure layout is not opaque, so callers can mutate internal offsets and error state. `off_t` in `struct nesting` and `struct asn1_data` requires suitable system headers from consumers. `ASN1_MAX_OIDS` is defined but not enforced by the visible writer.

## Test Signals

Compile tests should include this header from C files with the normal project includes. Behavioral tests come through `asn1.c` and any CLDAP or SPNEGO encoder tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.h -->

# sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.h

## Purpose

`libnet_unbecome_dc.h` declares the libnet request/response structure for demoting a DC from the directory's perspective.

## Important APIs, Types, and Functions

`struct libnet_UnbecomeDC` takes input `domain_dns_name`, `domain_netbios_name`, `source_dsa_address`, and `dest_dsa_netbios_name`; output is `error_string`.

## Control Flow

The implementation uses these four identifiers to locate a source DC, identify the destination DSA account, and remove DS server metadata.

## State and Persistence Behavior

The structure is transient, but the operation it describes mutates remote LDAP/DRSUAPI directory state.

## Dependencies and Integration Points

It is consumed by `libnet_unbecome_dc.c` and test code that pairs BecomeDC and UnbecomeDC workflows.

## Risks and Edge Cases

Inputs must be exact. A wrong destination NetBIOS name or source address could demote or attempt to remove the wrong directory objects. The output error string contract exists but current implementation does not populate it richly.

## Test Signals

Tests should assert failure on missing/wrong identifiers and successful cleanup after a controlled BecomeDC operation.

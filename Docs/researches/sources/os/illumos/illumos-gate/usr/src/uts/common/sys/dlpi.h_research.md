# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dlpi.h

## Scope

Complete file read, 1,632 lines. This header defines the Data Link Provider Interface, version 2.0, plus illumos/Solaris-specific DLPI extensions.

## Public Surface

The file exports:

- Sun DLPI ioctls such as `DLIOCRAW`, `DLIOCNATIVE`, `DLIOCMARGININFO`, `DLIOCIPNETINFO`, `DLIOCLOWLINK`, and `DLIOCHDRINFO`.
- `dl_ipnetinfo_t`.
- DLPI version constants.
- Primitive numbers for local management, Solaris notifications/capabilities/control, connectionless service, connection-oriented service, acknowledged connectionless service, XID/TEST, physical address, and statistics.
- DLPI state constants, error codes, media types, provider service modes, provider styles, originators, disconnect/reset reasons, acknowledged CL status masks, service classes, address types, flags, automatic XID/TEST flags, bind classes, promiscuous modes, and notification bits.
- QOS component structures, QOS range/selection structures, and `union DL_qos_types`.
- Capability definitions for checksum offload, zero-copy, DLD, VRRP, module-id wrapping, and related version/flag constants.
- STREAMS message layout typedefs for every DLPI primitive.
- `union DL_primitives`, allowing primitive inspection via the first `dl_primitive` field.
- `DL_*_SIZE` macros for each primitive structure.
- Kernel helper prototypes for building acknowledgments, checking module ids, attaching/binding/querying through LDI handles, and stringifying errors/primitives/MAC types.

## Behavior And Integration

DLPI providers and consumers use these definitions to exchange typed STREAMS protocol messages. Most message structures use offset/length pairs to refer to variable data that follows the fixed header in the same message block.

The capability section supports negotiation through `DL_CAPABILITY_REQ` and `DL_CAPABILITY_ACK`, including checksum offload and DLD fast function-call negotiation.

## Dependencies And Invariants

The header depends on `sys/types.h` and `sys/stream.h`. All primitive structures rely on the first member being `dl_primitive`. Offset/length fields must be validated against actual message size by consumers. Reserved/growth fields are expected to be zero.

## Risks

This is a broad ABI header: changing constant values, structure fields, or sizes can break drivers, STREAMS modules, and userland. Variable-length tail data is a common parsing risk. Kernel-only DLD/VRRP capability structures are hidden under `_KERNEL`, so code shared with userland must not assume they are always visible.

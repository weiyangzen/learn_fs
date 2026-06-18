# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/common.h

## Role

Common SBP-2 helper header for endian conversion, serial-bus address packing, ORB-pointer packing, and shared return codes.

## Key Elements

- Provides byte-swap macros for little-endian systems and no-op versions for big-endian systems.
- Defines `sbp2_addr_t` as two quadlets representing a 64-bit serial-bus address with node ID and aligned offset.
- Defines masks/shifts and `SBP2_ADDR_SET()`/`SBP2_ADDR2UINT64()` helpers.
- Defines `sbp2_orbp_t` as two quadlets representing an ORB pointer without node ID.
- Defines ORB null/offset masks and `SBP2_ORBP_SET()`/`SBP2_ORBP2UINT64()` helpers.
- Defines common SBP-2 return codes, aligned so success/failure match DDI success/failure.

## Dependencies and Coupling

Used by all SBP-2 headers. The swap macros depend on `_LITTLE_ENDIAN`.

## Research Notes

The address types are arrays of two 32-bit words, not native `uint64_t`, because SBP-2 ORB structures require quadlet alignment and wire-format ordering.

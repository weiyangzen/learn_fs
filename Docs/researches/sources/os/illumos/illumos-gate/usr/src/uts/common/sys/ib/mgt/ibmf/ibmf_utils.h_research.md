# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_utils.h

## Scope

Declares generic IBMF helper functions for packing and unpacking management datagram data.

## APIs

- `ibmf_utils_unpack_data()` unpacks raw MAD bytes into a host structure according to a format string, with source data and destination structure lengths.
- `ibmf_utils_pack_data()` packs a host structure into raw MAD bytes according to a format string, with structure and destination data lengths.

## Dependencies

- Used by IBMF/SAA code that needs structured conversion between host data and IB wire-format buffers.
- Format-string semantics are implemented in the corresponding source file, not this header.

## Risks And Invariants

- Callers must pass correct format strings and matching buffer sizes.
- These helpers are a central boundary between host-endian structures and MAD wire-format byte arrays.
- Incorrect lengths or format descriptors can corrupt protocol buffers or truncate decoded data.

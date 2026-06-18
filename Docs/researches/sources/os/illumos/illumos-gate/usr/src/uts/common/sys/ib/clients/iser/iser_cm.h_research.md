# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_cm.h

## Purpose

Declares the iSER Communications Manager event handler used with IBT CM events.

## Main Definitions

- Includes IBT and iSCSI protocol headers.
- Declares `iser_ib_cm_handler()`, taking CM private data, an IBT CM event, return arguments, return private-data buffer, and maximum return private-data length.

## Integration Notes

This is the narrow interface between iSER and the IBT communication manager. The handler is expected to translate IB CM events into iSER/IDM connection state transitions and optional private-data replies.

## Risks and Gotchas

- Return private data length is caller-provided; handler implementations must respect `ret_len_max`.
- CM handler behavior is tightly coupled to connection-stage values in `iser.h` and private-data layout in `iser_xfer.h`.

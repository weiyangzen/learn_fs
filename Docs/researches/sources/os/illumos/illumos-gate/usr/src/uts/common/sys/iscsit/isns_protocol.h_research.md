# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/isns_protocol.h

## Role

`isns_protocol.h` defines the wire-format constants and lightweight packet structures for iSNS traffic used by the iSCSI target service. It captures iSNS versioning, PDU sizing, function IDs, flags, response codes, attribute IDs, bitmaps, default IDs, name limits, and TLV/PDU structures.

## Major Definitions

The file sets protocol version `0x01`, default server port `3205`, a 12-byte PDU header, 4-byte response code, maximum payload size `65532`, and maximum PDU size as header plus payload. It defines iSNS function IDs for device attribute registration/query/get-next/deregister, SCN, discovery-domain and discovery-domain-set operations, ESI, heartbeat, and response forms.

Flag definitions cover first/last PDU, replace-registration, authentication block, server, and client flags. Response status constants cover success and protocol/server errors such as malformed messages, invalid registration/query/deregistration, unauthorized source, unsupported version/message, busy state, and unavailable ESI.

Attribute ID macros cover entity, portal, iSCSI node, portal group, discovery domain set, discovery domain, and DD feature attributes from iSNS drafts/RFC 4171. Additional masks define entity protocols, protocol version range packing, portal port/type bits, portal security bitmap bits, iSCSI node type bits, SCN bitmap bits, portal group tag bits, DDS status, DD bootlist, default PGT/DD IDs, and maximum/minimum name lengths.

The structures model variable-length packet data: `isns_tlv_t` is a TLV header with flexible first byte, `isns_packet_data_t` stores parsed header fields and an inline TLV array, `isns_reg_mesg_t` groups source/message/delimiter/operating attributes, `isns_resp_mesg_t` groups response status plus attributes, `isns_pdu_t` is the raw PDU header plus payload, and `isns_resp_t` is a response status plus data.

## Interfaces

There are no function prototypes. Consumers use these constants and structures to compose, parse, validate, and interpret iSNS PDUs.

## Integration Notes

This header is tightly coupled to network byte order handling and bounds checks in the implementation. The structures use one-byte trailing arrays for variable payloads, so callers must allocate and validate actual buffer sizes using the defined header, response, TLV, payload, and PDU size constants.

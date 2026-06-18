# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_protocol.h

## Role

`radius_protocol.h` defines the RADIUS RFC 2865 constants and raw packet shape needed by the iSCSI target RADIUS client code.

## Major Definitions

Packet code constants cover Access-Request, Access-Accept, and Access-Reject. Attribute constants cover User-Name, CHAP-Password, and CHAP-Challenge. The file defines the one-octet identifier length, 16-byte CHAP password string, 16-byte authenticator, maximum 253-byte attribute value, minimum 20-byte packet length, maximum 4096-byte packet length, and local shared-secret bounds of 16 to 128 bytes.

`radius_packet_t` models the raw wire packet: code, identifier, two-byte length, 16-byte authenticator, and variable data. `RAD_PACKET_HDR_LEN` is the fixed 20-byte header size.

## Interfaces

There are no function prototypes. Packet send/receive code includes this header to interpret packet bytes and validate field lengths.

## Integration Notes

The raw length field is byte-array based rather than a host-endian integer, which makes endian handling explicit in implementation code. The shared-secret maximum is a local policy even though the protocol has no defined upper bound.

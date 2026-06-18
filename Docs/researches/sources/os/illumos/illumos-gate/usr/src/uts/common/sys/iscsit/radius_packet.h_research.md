# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_packet.h

## Role

`radius_packet.h` defines the kernel-side packet description and send/receive entry points for iSCSI target RADIUS authentication. It builds on `radius_protocol.h` and represents decoded request/response attributes around illumos kernel sockets.

## Major Definitions

The file defines receive timing policy: `RAD_RCV_TIMEOUT` is five seconds per receive attempt and `RAD_RETRY_MAX` is two retries. `radius_attr_t` stores an attribute type code, value length, and a fixed maximum RADIUS attribute value buffer. `radius_packet_data_t` stores the RADIUS code, identifier, request/response authenticator, an attribute count, and a fixed four-element attribute array. The comment notes current outbound requests need only three attributes.

Response receive status values distinguish success, no data, timeout, protocol error, and authentication failure.

## Interfaces

`iscsit_snd_radius_request()` sends a request on a kernel socket to a RADIUS server IP/port using a populated packet descriptor and returns positive on success. `iscsit_rcv_radius_response()` receives and authenticates a response using the shared secret and original request authenticator, returning one of the local receive status codes and filling a packet descriptor.

## Integration Notes

This interface is part of the iSCSI target authentication path. Callers must enforce attribute count limits, shared-secret length constraints from `radius_protocol.h`, and authenticator validation; the fixed attribute array makes overflow checks straightforward but also constrains future RADIUS attribute expansion.

# File Research: sources/os/bsd/openbsd-src/sbin/iked/eap.h

`eap.h` defines EAP protocol structures, EAP code/type constants, MSCHAPv2 constants, packed MSCHAPv2 payload layouts, error codes, and external constmap declarations.

The structures cover generic EAP headers/messages, MSCHAP challenge, peer response, success, and failure payloads. Constants include IANA EAP method values and iked’s internal `EAP_TYPE_RADIUS`.

This header is consumed by `eap.c` and other IKEv2 code that needs to parse or construct EAP payloads inside IKE_AUTH.

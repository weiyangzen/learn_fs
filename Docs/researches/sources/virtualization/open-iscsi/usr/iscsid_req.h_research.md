# File Research: sources/virtualization/open-iscsi/usr/iscsid_req.h

## Purpose
`iscsid_req.h` declares management IPC helper APIs for talking to `iscsid` and uIP.

## Exports
The header defines `ISCSID_REQ_TIMEOUT`, forward-declares request/response and node-record structures, exposes the mutable `iscsid_namespace`, declares `iscsid_set_namespace()`, synchronous request execution, wait-by-fd, request-by-record and request-by-sid helpers, and `uip_broadcast()`.

## Integration Notes
The prototypes use `iscsiadm_cmd_e`, so consumers must include the management IPC command definitions before or alongside this header.

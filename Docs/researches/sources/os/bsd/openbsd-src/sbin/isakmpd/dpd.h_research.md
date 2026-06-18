# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.h

Public interface for Dead Peer Detection support.

Exports:
- `dpd_add_vendor_payload(struct message *)`
- `dpd_check_vendor_payload(struct message *, struct payload *)`
- `dpd_handle_notify(struct message *, struct payload *)`
- `dpd_start(struct sa *)`

The header forward-declares `message`, `payload`, and `sa`, keeping DPD integration independent of the full message/SA definitions at include sites.

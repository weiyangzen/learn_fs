# File Research: sources/virtualization/open-iscsi/usr/iser.h

## Purpose
`iser.h` declares the iSER connection setup helper.

## Exports
It forward-declares `struct iscsi_conn` and exports `iser_create_conn(struct iscsi_conn *conn)`.

## Integration Notes
The header is guarded by `ISER_TRANSPORT` and allows transport setup code to call the iSER-specific initializer without including full initiator internals in the header.

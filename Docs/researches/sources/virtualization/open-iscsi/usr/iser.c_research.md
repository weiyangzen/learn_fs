# File Research: sources/virtualization/open-iscsi/usr/iser.c

## Purpose
`iser.c` contains a transport-specific helper for iSER connection setup.

## API
`iser_create_conn(struct iscsi_conn *conn)` disables header digests by setting `conn->hdrdgst_en = ISCSI_DIGEST_NONE`, because iSER does not support header digests.

## Integration Notes
The file includes `initiator.h` for `struct iscsi_conn` and digest constants. It is intentionally tiny and likely referenced by transport template setup for iSER.

# File Research: sources/virtualization/open-iscsi/usr/be2iscsi.h

Small include guard and forward declaration header for `be2iscsi_create_conn(struct iscsi_conn *conn)`. It avoids including full initiator structures in users that only need the helper prototype.

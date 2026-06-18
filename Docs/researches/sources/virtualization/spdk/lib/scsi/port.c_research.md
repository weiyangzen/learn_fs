# File Research: sources/virtualization/spdk/lib/scsi/port.c

This file implements SCSI port allocation, construction, destruction, naming, and iSCSI TransportID formatting.

`spdk_scsi_port_create()` allocates a port and calls `scsi_port_construct()`; failure frees the allocation and returns `NULL`. `spdk_scsi_port_free()` tolerates a null pointer-to-pointer, clears the caller’s pointer, and frees the port. `scsi_port_construct()` validates the port name fits, marks the slot used, stores the numeric ID and index, and copies the name. `scsi_port_destruct()` clears the full port structure.

`spdk_scsi_port_get_name()` returns the stored port name.

`spdk_scsi_port_set_iscsi_transport_id()` builds an SPC-3 iSCSI initiator-port TransportID in code set format `0x01`. It clears the existing transport ID, fills protocol identifier and format, writes `<iscsi_name>,i,0x<isid>` with a 12-digit hex ISID, pads the name area to a 4-byte boundary, requires at least 20 bytes of additional length, writes that length big-endian, and stores total transport ID length.

The main boundary conditions are name length validation and ensuring the formatted iSCSI TransportID is padded and length-encoded correctly.

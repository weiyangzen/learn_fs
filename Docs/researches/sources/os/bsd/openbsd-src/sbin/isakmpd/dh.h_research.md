# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.h

This header defines DH group metadata, runtime group state, and the public DH API.

Key contents:
- `enum group_type`: MODP, EC2N, and ECP group classes.
- `struct group_id`: static group specification with type, ID, bit size, MODP parameters, and EC NID.
- `struct group`: runtime group object with ID, spec pointer, DH/EC backend pointers, and method callbacks.
- `DH_MAXSZ` set to 1024 bytes for 8192-bit groups.
- Prototypes for group initialization/free/lookup and DH exchange/shared-secret operations.

Research notes:
- The runtime `struct group` is backend-polymorphic through function pointers assigned in `group_get`.

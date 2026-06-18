# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.h

This header declares the connection management API.

Key contents:
- Prototypes for:
  - `connection_exist`
  - `connection_init`
  - `connection_passive_lookup_by_ids`
  - `connection_reinit`
  - `connection_report`
  - `connection_setup`
  - `connection_record_passive`
  - `connection_teardown`

Research notes:
- This API exposes active/passive connection lifecycle and lookup to the daemon and exchange handling code.

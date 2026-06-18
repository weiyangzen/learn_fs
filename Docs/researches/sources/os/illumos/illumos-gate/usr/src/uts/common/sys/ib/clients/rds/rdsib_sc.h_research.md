# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_sc.h

This legacy RDS service-console header defines path endpoint records and path notification hooks.

Core definitions:
- `rds_path_endpoint_t` records interface type, IP address, node IP address, and interface name.
- `rds_path_t` pairs local and remote endpoints.
- Hooks declare cluster interface naming and path up/down notifications.

Risk-sensitive invariants:
- Path lookup and path notifications connect RDS IB sessions to external cluster/service-console topology.
- Interface names are stored as pointers, so ownership/lifetime is external.

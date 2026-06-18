# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_sc.h

This RDSv3 service-console header mirrors the legacy RDS service-console path structures and hooks.

Core definitions:
- `rds_path_endpoint_t` records interface type, IP address, node IP address, and interface name.
- `rds_path_t` pairs local and remote endpoints.
- Path hooks declare cluster interface naming and path up/down notifications.

Risk-sensitive invariants:
- RDSv3 service-console integration shares struct names with legacy RDS, so include ordering and namespace expectations matter.
- Path notification callbacks are external integration points for link/topology changes.

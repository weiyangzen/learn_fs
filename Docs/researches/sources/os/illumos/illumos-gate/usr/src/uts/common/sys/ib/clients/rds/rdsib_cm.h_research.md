# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_cm.h

This small legacy RDS-over-IB CM header defines connection-management tuning constants.

Core definitions:
- `RDS_IB_PATH_RETRY` sets CM path retry count to 7.
- `RDS_IB_RNR_RETRY` uses infinite RNR retry.
- `RDS_IB_MAX_SGL` limits work requests to one SGL entry.
- `RDS_IB_PKT_LT` uses the packet lifetime from the path record.

Risk-sensitive invariants:
- These constants shape RC channel establishment and retry behavior.
- Single-SGL assumptions must match buffer construction in send/receive paths.

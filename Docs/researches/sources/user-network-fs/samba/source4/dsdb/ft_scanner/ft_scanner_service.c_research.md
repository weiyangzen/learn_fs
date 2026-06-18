# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.c

## Purpose

`ft_scanner_service.c` registers and initializes the `ft_scanner` task service. The service periodically scans inbound forest-transitive trusts from writable AD DCs and records discovered trusted-forest domain data into trust forest information.

## Important APIs, Types, and Functions

- `ft_scanner_connect_samdb()` obtains a system session and connects `service->l_samdb` to local samdb.
- `ft_scanner_task_init()` performs role gating, allocates `struct ft_scanner_service`, connects samdb, rejects RODCs, reads configuration intervals, schedules the startup timer, and registers the service IRPC name.
- `server_service_ft_scanner_init()` registers the service under name `"ft_scanner"`.

## Control Flow

Startup is role-gated. Standalone and domain-member roles terminate the task with `NT_STATUS_INVALID_DOMAIN_ROLE`; AD DCs continue. After service allocation, `startup_time` is recorded and the task's private data is set. A local samdb connection is opened as the system session. The code queries `samdb_rodc()` and refuses to run on RODCs because the scanner writes local trust metadata.

The service reads `ft_scanner:periodic_startup_interval` with a default of 15 seconds and `ft_scanner:periodic_interval` with a default of 900 seconds. The regular interval is clamped to at least 60 seconds. It then schedules the first scan with the startup interval and registers `"ft_scanner"` on the messaging context. There are no file-local IRPC handlers in this file.

## State and Persistence Behavior

Persistent effects are indirect. Initialization stores service state on the task talloc tree and opens samdb. Actual trust-object modifications occur in `ft_scanner_tdos.c`. Configuration values are read from loadparm at startup; changing them after startup will not affect the already stored interval unless the service is restarted.

## Dependencies and Integration Points

The file integrates with Samba's server service framework, auth system sessions, local samdb, loadparm, IRPC naming, and the scheduler from `ft_scanner_periodic.c`. It is compiled with the scanner implementation and generated local prototypes.

## Risks

The service must not run on RODCs or non-DC roles. Failing open would allow unauthorized or impossible writes. Startup failures terminate the task, which is appropriate for missing local samdb but can make deployment problems visible as service absence. The minimum 60 second regular interval protects against busy scan loops; tests should confirm this clamp.

## Test Signals

Tests should cover role-based startup decisions, RODC rejection, samdb connection failure handling, interval defaults and clamping, startup scheduling errors, IRPC name registration, and successful service registration details (`inhibit_fork_on_accept`, `inhibit_pre_fork`, task init pointer).

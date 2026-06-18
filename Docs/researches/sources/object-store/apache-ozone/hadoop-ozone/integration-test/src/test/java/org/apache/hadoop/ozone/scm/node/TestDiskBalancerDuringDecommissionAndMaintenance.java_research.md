# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerDuringDecommissionAndMaintenance.java

## Purpose
`TestDiskBalancerDuringDecommissionAndMaintenance` validates disk balancer behavior when datanodes enter decommissioning or maintenance states, including automatic pause, explicit stop while paused, and automatic resume only when appropriate.

## Important APIs, Types, and Functions
The test uses a 5-DN mini cluster, `ContainerOperationClient` decommission/maintenance/recommission calls, direct `DiskBalancerProtocol` DN proxies, `DiskBalancerConfigurationProto`, `DiskBalancerRunningStatus`, `NodeManager`, and `DiskBalancerService` log capture. Helpers include `stopDiskBalancer`, `getInServiceDatanodes`, and `queryAllInServiceDatanodes`.

## Control Flow, State, and Persistence
After each test, all DN disk balancers are stopped and verified `STOPPED`. The first test starts balancing on all DNs, decommissions one and starts maintenance on another, queries only in-service DNs to ensure excluded states do not appear, verifies service stop log messages, recommissions the decommissioned DN, and confirms it appears in reports/status and resumes. The second test starts balancing on a DN, decommissions it, verifies `PAUSED`, explicitly stops it, recommissions it, and verifies it stays `STOPPED`. The third decommissions an initially stopped DN, starts disk balancer while decommissioning, verifies it becomes `PAUSED`, then recommissions and verifies it becomes `RUNNING`.

## Dependencies and Integration Points
This integrates SCM node operational state transitions, DN persisted operation state, disk balancer service lifecycle, direct DN RPC status, CLI-equivalent filtering for in-service DNs, and log messages from `DiskBalancerService`.

## Risks and Test Signals
Risks include brittle log text checks, state transition timing, and cross-test contamination if cleanup fails. Signals include direct service status, SCM node-state waits, in-service query filtering, and explicit log evidence for pause/resume decisions.

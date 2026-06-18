# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfigKeys.java

## Purpose
Centralizes SCM and container-service configuration key constants and defaults. It spans SCM HA, Ratis, container layout/chunking, RPC/HTTP addresses, datanode directories, heartbeat and node liveness, pipeline placement/limits, block deletion, network topology, balancer/admin monitors, event queues, audit logging, and SCM HA Ratis tuning.

## Important APIs, Types, And Functions
`ScmConfigKeys` is a public unstable constants holder. Notable groups include `OZONE_SCM_HA_PREFIX`, `OZONE_SCM_DB_DIRS`, Ratis container keys (`HDDS_CONTAINER_RATIS_*`), SCM service ports and bind hosts, liveness intervals, `OZONE_SCM_NAMES`, HA service/node ID keys, pipeline placement and timeout keys, topology schema keys, Ratis HA keys, and `HDDS_SCM_HTTP_AUTH_TYPE`.

## Control Flow
There is no executable logic beyond a private constructor. Runtime services import constants when reading configuration.

## State And Persistence
No state is stored here. The string constants define externally persisted Ozone configuration names and default values.

## Dependencies And Integration Points
Depends on HDDS audience/stability annotations and Ratis `TimeDuration`. It is widely integrated by SCM, datanode, clients, HA bootstrap, Ratis server setup, topology loading, admin services, and tests.

## Risks And Test Signals
Changing constants or defaults is a compatibility risk for deployed clusters. Some defaults are intentionally high or workaround-driven, such as Ratis log purge gap. Tests should cover config key resolution, address/port fallback, HA suffix handling, and upgrade compatibility.

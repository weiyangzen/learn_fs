<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java

Purpose: Prepares all OMs in an HA service for upgrade or downgrade by asking OM to apply pending transactions, snapshot at a quorum transaction, purge logs, and then polling individual OMs until a majority or all complete.

Important APIs and types: `OzoneManagerProtocol.prepareOzoneManager`, `getOzoneManagerPrepareStatus`, `PrepareStatusResponse`, `PREPARE_COMPLETED`, `OmUtils.getOmHostsFromConfig`, `OMAdmin.createOmClient`, `Time.monotonicNow`, duration options, and deprecated hidden timing aliases.

Control flow: `execute()` calls `prepareOzoneManager(waitTimeout, checkInterval)` and prints the returned transaction ID. It builds a map of configured OM hosts to unprepared, then loops until timeout or all hosts prepare. Each iteration opens a single-OM client, queries status for the prepare transaction, logs status and transaction index, records completed hosts, catches per-host IOExceptions, and sleeps between rounds. After the loop it throws if fewer than a majority prepared; otherwise it prints success and any remaining unprepared hosts.

State and persistence behavior: Local state is the host-prepared map and timing values. Remote durable state is the OM prepare barrier, Ratis snapshot/log purge, and write rejection until cancellation or finalization. Deprecated option values are resolved only for the invocation.

Dependencies and integration points: Requires an explicit OM service ID; uses parent OM admin to create per-host clients and Ozone configuration to enumerate hosts.

Risks: Majority success can leave minority OMs unprepared, which is reported but still exits successfully. Per-host IOExceptions are swallowed during polling until majority logic fails. Hidden timing options and deprecated aliases can make tests brittle if defaults change.

Test signals: Mock transaction ID, per-host completed/in-progress/error status, majority vs minority completion, timeout behavior, deprecated timing option resolution, and emitted waiting/success/failure messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java -->

## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconSafeModeMgrTask.java

Purpose: startup task that waits for Recon to observe enough SCM/container state before exiting Recon safe mode.

Important APIs/types/functions: constructor captures managers, wait threshold, and datanode heartbeat interval; `start()` loops until safe mode exits or threshold is exceeded; `tryReconExitSafeMode()` compares known containers against containers reported by all datanodes.

Control flow: initial check runs immediately. While still in safe mode and within threshold, the synchronized `start` method waits for one heartbeat interval, refreshes nodes/containers, and retries. If all containers are represented by datanode reports, safe mode is disabled; otherwise threshold expiry forces exit with a warning.

State and persistence: no durable writes except `ReconSafeModeManager.setInSafeMode(false)`. Dependencies are `ContainerManager`, `ReconNodeManager`, `ReconSafeModeManager`, task config, and heartbeat config.

Risks: compares only container counts, not exact identity coverage beyond the set size built from datanodes; initial node/container lists can be stale until refreshed. `wait` requires the synchronized method, which is present. Tests should cover no nodes, no containers, complete coverage, forced timeout exit, node-not-found logging, and interruption.

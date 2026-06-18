<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java

## Purpose
`ReconfigurableBase` is an HDDS base class for Hadoop-style dynamic runtime reconfiguration.

## Important APIs, Types, and Functions
It extends `Configured` and implements `Reconfigurable`. Important fields include `reconfigThread`, `shouldRun`, `reconfigLock`, `startTime`, `endTime`, `status`, and completion callbacks. APIs include abstract `getNewConf`, `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, final `reconfigureProperty`, abstract `getReconfigurableProperties`, `isPropertyReconfigurable`, abstract `reconfigurePropertyImpl`, nested `ReconfigurationThread`, and `addReconfigurationCompleteCallback`.

## Control Flow
`startReconfigurationTask` rejects stopped or already-running tasks, starts a daemon thread, and records start time. The thread loads new config, computes changed properties, redacts log values, skips non-reconfigurable changes, applies reconfigurable ones through `reconfigurePropertyImpl`, updates old config, records optional error messages, marks end time/status, clears the thread, and invokes callbacks. Direct `reconfigureProperty` applies one property under the configuration lock.

## State and Persistence Behavior
Runtime state records task lifecycle and last status. Applied changes mutate the in-memory `Configuration`; persistence back to config files is not handled here.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `Reconfigurable`, `ReconfigurationUtil`, `ReconfigurationTaskStatus`, `ConfigRedactor`, Guava `Maps`, and subclasses that define supported properties and reload sources.

## Risks and Test Signals
Risks include callback execution under `reconfigLock`, `shutdownReconfigurationTask` joining a thread after clearing the field, callbacks calling status while lock is held, and in-memory changes diverging from files. Tests should cover concurrent start rejection, status while running/finished, non-reconfigurable skips, exception capture, callback behavior, shutdown, and redaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java -->

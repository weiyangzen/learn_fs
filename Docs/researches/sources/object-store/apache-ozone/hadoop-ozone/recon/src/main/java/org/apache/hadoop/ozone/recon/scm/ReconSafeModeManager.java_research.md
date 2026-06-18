## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSafeModeManager.java

Purpose: this is Recon's minimal `SafeModeManager` implementation. It tracks whether Recon SCM tasks should be considered in safe mode without implementing SCM's full safe-mode rule engine.

Important APIs and types: implements `SafeModeManager`, stores an `AtomicBoolean inSafeMode`, exposes `getInSafeMode`, and adds `setInSafeMode`.

Control flow: the facade creates this manager and passes it to pipeline report handling and `ReconSafeModeMgrTask`. On startup, regular Recon SCM tasks are started only if `getInSafeMode` is false.

State and persistence: one in-memory boolean, defaulting to true. There is no durable safe-mode state.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade`, `ReconPipelineReportHandler`, and `ReconSafeModeMgrTask`. It is a passive gate for tasks rather than a full SCM safety subsystem.

Risks and edge cases: default true means tasks will not start until another component clears safe mode. There are no listeners, rule details, or persisted transition records. External code must manage transitions correctly.

Test signals: no direct test was found. Tests should cover default state, setter visibility, and facade behavior when safe mode is true or false at startup.

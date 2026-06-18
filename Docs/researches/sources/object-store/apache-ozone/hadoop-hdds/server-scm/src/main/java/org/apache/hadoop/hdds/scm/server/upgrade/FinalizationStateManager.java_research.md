# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationStateManager.java

Purpose: This interface owns the replicated state transitions for SCM upgrade finalization. It is the HA/Ratis handler that adds or removes the finalizing mark, finalizes a layout feature, and reports checkpoint progress.

Important APIs and types: Replicated methods are annotated with `@Replicate`: `addFinalizingMark`, `removeFinalizingMark`, and `finalizeLayoutFeature(Integer)`. Non-replicated methods include `crossedCheckpoint`, `getFinalizationCheckpoint`, `setUpgradeContext`, and `reinitialize`. As an `SCMHandler`, it returns Ratis request type `FINALIZE`.

Control flow: `SCMUpgradeFinalizer` calls the replicated methods on the leader-facing proxy. Ratis applies the operations across SCMs so followers update the finalizing mark, layout versions, and VERSION files consistently. Snapshot installation calls `reinitialize` with a new finalization table.

State and persistence behavior: The interface describes mutations to the finalization metadata table and local layout version. The actual implementation keeps an in-memory mark synchronized with the transaction buffer because DB flushes can be asynchronous.

Dependencies and integration points: It integrates upgrade finalization with SCM HA request routing, generated invokers, DB tables, and the SCM context used by other services.

Risks: The replicated annotation is a critical contract. Adding new finalization mutations without `@Replicate` would break HA consistency. The `FINALIZE` request type must match the Ratis state machine's dispatch rules.

Test signals: Tests should verify replicated methods are invoked through the generated proxy, request type is `FINALIZE`, and checkpoint queries reflect the persistent state after add/finalize/remove transitions.

# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeExitRule.java

Purpose: This abstract base class defines the common event-driven lifecycle for SCM safe mode exit rules. A concrete rule subscribes itself to an `EventQueue`, receives events as an `EventHandler<T>`, updates rule-local state, and notifies `SCMSafeModeManager` when its condition is satisfied.

Important APIs and types: The constructor stores the owning `SCMSafeModeManager`, derives `ruleName` from the class name, and registers `this` against the concrete `TypedEvent<T>` returned by `getEventType()`. Subclasses implement `validate()`, `process(T report)`, `cleanup()`, `getStatusText()`, and `refresh(boolean forceRefresh)`. The base class exposes `getRuleName()`, `scmInSafeMode()`, `getSafeModeMetrics()`, and a feature flag `validateBasedOnReportProcessing`.

Control flow: `onMessage` is final. If SCM is still in safe mode, it first validates before processing, then processes the event only if still unsatisfied, and validates again. On either successful validation it calls `safeModeManager.validateSafeModeExitRules(ruleName)` and then `cleanup()`. This makes each concrete rule idempotent around repeated or late reports.

State and persistence behavior: The class keeps only in-memory rule metadata and the report-processing validation flag. Persistence is delegated to managers and event handlers outside this file. Cleanup is subclass-defined and usually clears sampled containers, pipelines, or report-tracking sets.

Dependencies and integration points: It integrates the safe mode manager with the HDDS event framework. Subclasses such as datanode, container, pipeline, and state-machine readiness rules use this template to bind SCM startup reports to safe mode exit.

Risks: Rule handlers remain registered because there is no handler removal path, so every message checks `getInSafeMode()` defensively. A subclass with non-idempotent `process` or `cleanup` can miscount reports if events are duplicated. The temporary `validateBasedOnReportProcessing` flag marks an active migration path and can hide behavior differences during HDDS-11958 work.

Test signals: Useful tests should send events before and after satisfaction, verify `process` is skipped when pre-validation succeeds, verify `cleanup` runs once per satisfied rule transition, and confirm late events after safe mode exit do not mutate rule state.

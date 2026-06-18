# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeManager.java

Purpose: This is the minimal interface for components that expose safe mode status. It abstracts the common question "is this component in safe mode?" without tying callers to the concrete SCM safe mode manager implementation.

Important APIs and types: The single method `boolean getInSafeMode()` returns the current safe mode state. `SafeModeExitRule` consumes this method through `SCMSafeModeManager`, and external components can depend on the interface when only status is needed.

Control flow: There is no internal control flow. Implementations are responsible for providing a consistent view of safe mode state, usually backed by `SCMContext` or the concrete `SCMSafeModeManager`.

State and persistence behavior: The interface owns no state and has no persistence. State semantics are defined by implementers.

Dependencies and integration points: It is part of the `org.apache.hadoop.hdds.scm.safemode` package and acts as a small contract between safe mode-aware code and SCM services.

Risks: The interface does not distinguish manual forced exit, normal rule-based exit, pre-check failures, or startup not-yet-initialized states. Callers needing those details must use richer SCM APIs.

Test signals: Tests for implementers should verify the returned boolean changes on normal exit, force exit, and startup initialization paths.

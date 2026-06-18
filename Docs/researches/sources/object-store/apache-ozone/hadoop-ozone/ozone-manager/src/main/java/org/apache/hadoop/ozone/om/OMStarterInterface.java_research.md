# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStarterInterface.java

Purpose: `OMStarterInterface` is a small dependency-injection seam for `OzoneManagerStarter`, allowing CLI code to invoke OM lifecycle commands without directly coupling to the concrete starter implementation.

Important APIs and types: it declares `start`, `init`, `bootstrap`, and `startAndCancelPrepare`. All methods accept `OzoneConfiguration`; `bootstrap` also accepts `force`. Methods throw `IOException` and `AuthenticationException`.

Control flow: none inside the interface. Implementations own startup, initialization, HA bootstrap, and start-with-prepare-cancel behavior.

State and persistence: no state. Implementations will affect OM storage, security login, and cluster metadata.

Dependencies and integration points: used by command-line bootstrapping and tests that inject alternate starters. Depends only on `OzoneConfiguration` and Hadoop authentication exception types.

Risks: lifecycle semantics are encoded only in method names and implementations. Tests should catch mismatches between CLI flags and invoked interface methods. Since exceptions are broad, callers need to present clear user-facing errors.

Test signals: CLI unit tests can mock this interface to verify `start`, `init`, forced bootstrap, and prepare-cancel flows are dispatched with the expected configuration and flags.

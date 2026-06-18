<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java

Purpose: `SCMSafeModeManager` coordinates SCM startup safe mode. It tracks rule validation, precheck completion, safe-mode exit, periodic status logging, safe-mode metrics, and notifications to delayed SCM services.

Important APIs and types: It implements `SafeModeManager` and exposes `start`, `stop`, `validateSafeModeExitRules`, `forceExitSafeMode`, `refresh`, `refreshAndValidate`, `getInSafeMode`, `getRuleStatus`, `getPreCheckComplete`, `reconfigureLogInterval`, and nested enum `SafeModeStatus`. It uses `SafeModeRuleFactory`, `SafeModeExitRule`, `SCMServiceManager`, `SCMContext`, `SafeModeMetrics`, and `EventQueue`.

Control flow: Construction initializes rule factory, records exit and precheck rules, creates metrics, and optionally disables safe mode immediately. `start` records entry time and starts periodic logging. Rule validation moves state from INITIAL to PRE_CHECKS_PASSED when all precheck rules pass, then to OUT_OF_SAFE_MODE when all rules pass. Exiting safe mode updates context, stops logging, notifies services, and records duration. Refresh methods either rebuild rule state or rebuild and validate immediately.

State and persistence behavior: State is process-local: atomic status, rule maps, validated rule sets, metrics, log scheduler, and entry timestamp. No durable state is written, but the rules read SCM DB-backed manager state during refresh and validation.

Dependencies and integration points: It is the central safe-mode service used by SCM startup, service gating, protocol status APIs, and metrics. It notifies `SCMServiceManager` when prechecks pass or safe mode exits, and updates `SCMContext` for cluster-wide status.

Risks: The rule factory is singleton-based, so initialization order and tests must isolate it. Periodic logging calls every rule's status text, which may query managers and produce expensive logs. `forceExitSafeMode` bypasses rule validation. `getCurrentContainerThreshold` hard-casts the Ratis rule by name and is marked temporary.

Test signals: Tests should cover disabled safe mode, precheck transition, final exit transition, service notifications, forced exit duration recording, refresh and refresh-and-validate behavior, periodic logger start/stop/reconfiguration, metrics unregister, and rule status reporting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SCMSafeModeManager.java -->

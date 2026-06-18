# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnosticProbe.java

Purpose: `DiagnosticProbe` defines the contract for Kerberos diagnostic checks.

Important APIs and types: It declares `name()` and `test(OzoneConfiguration)` returning `ProbeResult`.

Control flow: Implementations are invoked by `DiagnoseSubcommand` in fixed order.

State and persistence behavior: The interface itself has no state. Implementations may read config, environment, filesystem, or JVM state.

Dependencies and integration points: This abstraction allows new probes to be added to the diagnose flow with consistent naming and result classification.

Risks: No severity detail beyond PASS/WARN/FAIL is available, so richer diagnostics must be printed as text.

Test signals: Probe implementations satisfy the interface and return meaningful `ProbeResult` values.

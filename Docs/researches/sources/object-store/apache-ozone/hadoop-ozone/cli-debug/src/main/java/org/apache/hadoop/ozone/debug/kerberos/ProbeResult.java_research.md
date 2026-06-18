# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ProbeResult.java

Purpose: `ProbeResult` is the three-state severity enum for Kerberos diagnostic probes.

Important APIs and types: It defines `PASS`, `WARN`, and `FAIL`.

Control flow: `DiagnoseSubcommand` switches on this enum to print status lines, count summary values, and choose exit code.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Every `DiagnosticProbe` returns this enum.

Risks: The model has no field for remediation, machine-readable details, or skipped/not-applicable states; those must be expressed in text.

Test signals: Exhaustive switch behavior in diagnose and stable enum names in output.

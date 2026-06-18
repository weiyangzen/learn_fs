# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnoseSubcommand.java

Purpose: `DiagnoseSubcommand` runs the ordered Kerberos diagnostic suite and summarizes PASS/WARN/FAIL counts.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Integer>`, uses `OzoneConfiguration`, `DiagnosticProbe`, `ProbeResult`, and concrete probe classes.

Control flow: `call()` prints a header, builds a fixed probe list, and executes each probe serially. During each probe it temporarily redirects `System.out` and `System.err` into a UTF-8 buffer, restores streams, prints probe output through command output, increments result counters, and returns exit code 1 if any probe fails.

State and persistence behavior: It reads configuration, environment, filesystem, and JVM state through probes. It mutates global system streams temporarily and restores them in `finally`.

Dependencies and integration points: It is a subcommand of `KerberosSubcommand` and coordinates all probe contracts.

Risks: Temporarily redirecting global streams is process-wide and unsafe under concurrent command execution. Catching `Throwable` keeps diagnostics robust but may mask serious errors as probe failures.

Test signals: Probe headers, per-probe status lines, summary counts, and return code 1 when failures are present.

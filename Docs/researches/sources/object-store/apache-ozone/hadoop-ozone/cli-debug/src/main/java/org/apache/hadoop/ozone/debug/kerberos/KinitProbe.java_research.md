# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KinitProbe.java

Purpose: `KinitProbe` verifies that the `kinit` executable is available and executable on `PATH`.

Important APIs and types: It extends `ConfigProbe`, uses `System.getenv("PATH")`, `File.exists`, and `File.canExecute`.

Control flow: The probe prints PATH, returns FAIL if PATH is unset, scans each colon-separated directory for `kinit`, returns FAIL if found but not executable, PASS if executable, and FAIL if not found.

State and persistence behavior: It reads environment and filesystem metadata only.

Dependencies and integration points: It helps distinguish ticket/config problems from a missing Kerberos client utility during diagnostics.

Risks: The path separator is hard-coded as `:`, matching Unix-like deployments but not Windows. It does not run `kinit`, only checks existence/executability.

Test signals: PASS with executable `kinit`, FAIL for unset PATH, non-executable found file, or missing executable.

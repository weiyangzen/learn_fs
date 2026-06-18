# sources/user-network-fs/smbj/gradlew

Source read signal: reviewed complete local file (160 lines, 4971 bytes).

## Purpose
`gradlew` covers Gradle wrapper launcher. is the POSIX shell wrapper that locates Java, resolves `gradle-wrapper.jar`, normalizes paths under Cygwin/MSYS/Darwin/NonStop, sets JVM options, and invokes `org.gradle.wrapper.GradleWrapperMain`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The script parses app-relative paths, validates `java`, builds an argument array, escapes paths for Windows-like shells, then execs Java with wrapper classpath and user arguments.

## State and persistence
No project runtime state; it uses environment variables such as `JAVA_HOME`, `DEFAULT_JVM_OPTS`, `GRADLE_OPTS`, and `JAVA_OPTS`.

## Dependencies and integration points
Integrates with the checked-in Gradle wrapper jar/properties and shell environments used by CI and developers.

## Risks
Wrapper correctness depends on executable bits, matching wrapper jar, and shell portability. Environment options can change memory/daemon behavior.

## Test signals
Signals are `./gradlew --version`, CI `./gradlew check`, and successful use on Linux/macOS/Windows compatibility shells.

# sources/user-network-fs/smbj/src/test/resources/logback-test.xml
# sources/user-network-fs/smbj/src/test/resources/logback-test.xml

Purpose: test logging configuration for the SMBJ module. It defines Logback appenders/loggers used while running tests, typically routing output to console with controlled levels.

State and persistence: runtime logging configuration only; no application state. Dependencies are Logback XML schema/classes and test runtime classpath discovery. Integration point is all tests in the module because `logback-test.xml` is auto-detected. Risks include overly verbose logs obscuring failures, suppressing useful diagnostics, or changing package log levels in ways that affect timing-sensitive tests. Test signal is configuration-level, not executable assertions.

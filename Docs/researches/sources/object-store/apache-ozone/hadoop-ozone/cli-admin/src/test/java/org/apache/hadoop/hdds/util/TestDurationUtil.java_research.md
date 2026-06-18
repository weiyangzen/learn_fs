# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/util/TestDurationUtil.java

Purpose: This compact parameterized suite locks down the formatting contract of `DurationUtil.getPrettyDuration`.

Important APIs and types: It uses Java `Duration`, JUnit parameterized tests, `Arguments`, and `DurationUtil`.

Control flow: Positive cases map durations from zero through days and `Long.MAX_VALUE` seconds to expected strings. Negative cases pass negative durations and expect `IllegalStateException`.

State and persistence behavior: There is no runtime state beyond immutable `Duration` objects and no persistence.

Dependencies and integration points: The utility output likely appears in CLI/admin reporting where stable hour/minute/second formatting matters.

Risks: The test covers second precision only and does not document fractional duration handling. The `Long.MAX_VALUE` case guards overflow-prone conversion.

Test signals: Exact strings such as `0s`, `1m 0s`, `24h 0m 0s`, and rejection of negative durations including `Long.MIN_VALUE` seconds.

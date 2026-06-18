# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/TestLeakDetector.java

## Purpose
Tests the DB package `LeakDetector` utility.

## Important APIs, types, and functions
- Uses the `LeakDetector` class from `org.apache.hadoop.hdds.utils.db` and JUnit assertions.
- The single test named `test` validates expected leak detector behavior.

## Control flow
The test creates detector-managed resources or markers and verifies the detector reports expected non-leak/leak behavior according to its API.

## State and persistence behavior
State is in-memory detector tracking. No external persistence.

## Dependencies and integration points
The detector is related to DB codec/buffer lifecycle checks where unclosed buffers are a risk.

## Risks and test signals
If leak detection fails, DB buffer leaks may go unnoticed or tests may become flaky. This file provides a focused detector smoke test.

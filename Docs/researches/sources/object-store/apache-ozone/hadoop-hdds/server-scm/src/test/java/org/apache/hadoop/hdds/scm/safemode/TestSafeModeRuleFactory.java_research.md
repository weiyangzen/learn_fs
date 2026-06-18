# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeRuleFactory.java

## Purpose
`TestSafeModeRuleFactory` validates initialization and loaded-rule counts for the singleton `SafeModeRuleFactory`. It also ensures accessing the factory before initialization is illegal.

## Important APIs, Types, and Functions
- `SafeModeRuleFactory.initialize`, `getInstance`, `addSafeModeManager`, `getSafeModeRules`, and `getPreCheckRules` are under test.
- Reflection resets the private static `instance` field for the illegal-state test.
- `initializeSafeModeRuleFactory` supplies mocked `SCMSafeModeManager`, pipeline/container/node managers, and a real event queue.

## Control Flow
The first test clears the singleton and asserts `getInstance` throws. The loaded-rule tests initialize the factory, attach a safe-mode manager, and assert hardcoded counts: five safe-mode rules and one precheck rule.

## State and Persistence Behavior
State is singleton/global JVM state only. No persistence is used.

## Dependencies and Integration Points
The factory depends on configuration, SCM context, event queue, pipeline manager, container manager, node manager, and safe-mode metrics. This file is sensitive to factory initialization order across tests.

## Risks and Edge Cases
The test explicitly handles prior initialization by resetting the singleton. Hardcoded rule counts are brittle but intentionally document current factory behavior until rules are loaded differently.

## Test Signals
Failures signal either unexpected rule-set changes or unsafe singleton access before initialization.

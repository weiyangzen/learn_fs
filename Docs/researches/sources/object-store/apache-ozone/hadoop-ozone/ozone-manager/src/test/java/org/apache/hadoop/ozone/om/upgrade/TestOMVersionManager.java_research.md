# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMVersionManager.java

## Purpose
`TestOMVersionManager` validates OM layout version manager invariants: initial feature allowance, unsupported version rejection, monotonic layout versions, aspect compatibility with request pre-execution, and upgrade action registration.

## Important APIs, Types, and Functions
- `OMLayoutVersionManager` manages metadata layout version and feature allowance.
- `OMLayoutFeature` enum values must have consecutive `layoutVersion()` values.
- `OMClientRequest.preExecute` must have `OzoneManager` as its first parameter for aspect compatibility.
- `registerUpgradeActions(OM_UPGRADE_CLASS_PACKAGE)` discovers `@UpgradeActionOm` classes.
- Nested `MockOmUpgradeAction` executes by calling `OzoneManager.getVersion`.

## Control Flow
The tests instantiate default and explicit-version managers, assert initial allowance, and verify an unsupported version greater than the latest feature throws `OMException` with `NOT_SUPPORTED_OPERATION`. The enum ordering test iterates every feature and asserts versions increase by one. It also attaches and executes an action on the last feature. The compatibility test reflectively inspects `OMClientRequest.preExecute`. The registration test mocks an old metadata layout version and ensures `INITIAL_VERSION` gains the nested action.

## State and Persistence Behavior
No durable state is written. Feature action registration mutates static/enum-associated action state for `OMLayoutFeature`, which can affect test ordering if not carefully controlled by the manager's registration semantics.

## Dependencies and Integration Points
The file depends on layout feature enums, annotation scanning, OM request base class reflection, `OMException`, and `OzoneManager`. It is a guard for upgrade framework metadata consistency.

## Risks and Edge Cases
The tests cover monotonic version numbering and registration when metadata layout is behind. They do not validate every real upgrade action's side effects. Because enum action state can be mutable, tests must avoid assumptions that actions are always absent after registration in the same JVM.

## Test Signals
The file provides high-value regression protection against accidental layout version gaps and preExecute signature changes that would break aspect gating.

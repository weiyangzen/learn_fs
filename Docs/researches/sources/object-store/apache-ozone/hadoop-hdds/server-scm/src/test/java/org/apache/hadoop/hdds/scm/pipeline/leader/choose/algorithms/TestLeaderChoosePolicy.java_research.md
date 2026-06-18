# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/TestLeaderChoosePolicy.java

## Purpose
`TestLeaderChoosePolicy` verifies leader-election policy loading inside `RatisPipelineProvider`. It confirms the default policy class and the failure behavior for a nonexistent configured policy.

## Important APIs, Types, and Functions
- `RatisPipelineProvider.getLeaderChoosePolicy` is inspected.
- `ScmConfigKeys.OZONE_SCM_PIPELINE_LEADER_CHOOSING_POLICY` configures the policy class.
- `MinLeaderCountChoosePolicy` is the expected default.

## Control Flow
The default test constructs a provider with mocked node manager, state manager, event publisher, and empty SCM context, then asserts the policy class. The invalid-class test sets a bogus class name and expects provider construction to throw `RuntimeException`.

## State and Persistence Behavior
No persistence is used. Configuration controls construction-time policy selection.

## Dependencies and Integration Points
This test binds `RatisPipelineProvider` initialization to leader choose policy configuration and `SCMContext`.

## Risks and Edge Cases
Unlike pipeline choose policy factory tests, invalid leader policy configuration is expected to fail hard. The test does not cover a valid custom implementation.

## Test Signals
The test provides a narrow but important signal that default Ratis leader selection remains min-leader-count based and invalid configuration is not silently ignored.

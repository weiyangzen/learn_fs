# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestPipelineChoosePolicyFactory.java

## Purpose
`TestPipelineChoosePolicyFactory` verifies that SCM loads the correct pipeline choose policy for replicated and EC requests, and falls back to defaults when configured classes are missing or invalid.

## Important APIs, Types, and Functions
- `PipelineChoosePolicyFactory.getPolicy(nodeManager, scmConfig, isEC)` is the main API.
- Defaults `OZONE_SCM_PIPELINE_CHOOSE_POLICY_IMPL_DEFAULT` and `OZONE_SCM_EC_PIPELINE_CHOOSE_POLICY_IMPL_DEFAULT` are asserted.
- Nested `DummyImpl` has an invalid constructor; `DummyGoodImpl` is a valid policy implementation.
- `ScmConfig.setPipelineChoosePolicyName` and `setECPipelineChoosePolicyName` drive configuration.

## Control Flow
Setup loads `ScmConfig` from a default `OzoneConfiguration` and creates a mock node manager. Tests request default policies, configure a valid EC policy, configure invalid constructor classes, and configure nonexistent classes. Assertions compare exact policy classes.

## State and Persistence Behavior
No persistence is involved. State consists of mutable `ScmConfig` policy-class names.

## Dependencies and Integration Points
The test covers reflective class loading and policy initialization against a `NodeManager`. It is important for operational config compatibility because bad class names should not prevent SCM from choosing a default policy.

## Risks and Edge Cases
The class checks invalid constructor and class-not-found fallback, but not class-cast errors or constructor exceptions thrown from a valid signature. It asserts fallback rather than exception for these invalid configurations.

## Test Signals
The exact class identity assertions provide a clear regression signal for default and EC-specific policy behavior.

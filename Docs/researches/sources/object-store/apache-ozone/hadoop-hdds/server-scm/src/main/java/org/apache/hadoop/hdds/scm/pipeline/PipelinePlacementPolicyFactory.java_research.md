# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicyFactory.java

## Purpose
`PipelinePlacementPolicyFactory` instantiates the configured pipeline placement policy implementation.

## Important APIs, Types, And Functions
`getPolicy` reads `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY` from configuration, defaulting to `PipelinePlacementPolicy`, and reflectively invokes a constructor accepting `NodeManager`, `PipelineStateManager`, and `ConfigurationSource`.

## Control Flow
The factory resolves the class, attempts constructor lookup and instantiation, and wraps any exception in a `RuntimeException` identifying the failed class.

## State And Persistence Behavior
It is a stateless utility class with a private constructor.

## Dependencies And Integration Points
It depends on `PlacementPolicy`, SCM config keys, `NodeManager`, `PipelineStateManager`, and `ConfigurationSource`. Pipeline providers use it to decouple placement algorithm selection from construction.

## Risks And Edge Cases
Custom placement policies must provide the exact constructor signature or SCM startup fails at runtime. Exceptions are unchecked, so configuration mistakes surface as service initialization failures.

## Test Signals
Tests should verify default policy construction, custom policy construction, wrong-class/wrong-constructor failure, and propagation of constructor exceptions.

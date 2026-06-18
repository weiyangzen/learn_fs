# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedTimeCostProvider.java

## Purpose
`WeightedTimeCostProvider` computes the scheduler cost of an RPC as a weighted sum of its `ProcessingDetails` timing buckets. It is intended for use by cost-aware schedulers such as `DecayRpcScheduler`.

## Important APIs, types, and functions
- Config prefix `.weighted-cost.` is appended to the IPC namespace and lowercase `ProcessingDetails.Timing` name.
- Defaults bill `LOCKFREE`, `RESPONSE`, and `HANDLER` at weight 1, `LOCKSHARED` at 10, `LOCKEXCLUSIVE` at 100, and all other timing fields at 0.
- `init(String namespace, Configuration conf)` allocates one weight per timing enum and reads per-timing integer overrides.
- `getCost(ProcessingDetails details)` multiplies each recorded timing value by its configured weight and returns the sum.

## Control flow
Initialization iterates over all timing enum values, chooses a default by switch, builds the config key, and stores the configured weight. Cost calculation iterates over the same enum order and accumulates `details.get(timing) * weights[ordinal]`.

## State and persistence behavior
The provider stores only its configured `long[] weights`. It does not persist data and should be initialized before use.

## Dependencies and integration points
It implements `CostProvider`, depends on `ProcessingDetails`, and is selected through the Hadoop IPC cost-provider config key. It integrates with schedulers that use per-call cost rather than simple request counts.

## Risks and edge cases
`getCost` uses an `assert` to enforce initialization, so production JVMs without assertions can turn uninitialized use into a `NullPointerException`. Negative weights are not rejected and could create negative costs. Large timing values and weights can overflow `long`. Config uses `getInt`, so weights are integer-bounded even though stored as long.

## Test signals
Tests should verify default weights, per-timing override keys, ignored queue/wait timing defaults, cost units, uninitialized behavior, negative/large weights, and integration with `DecayRpcScheduler` cost accounting.

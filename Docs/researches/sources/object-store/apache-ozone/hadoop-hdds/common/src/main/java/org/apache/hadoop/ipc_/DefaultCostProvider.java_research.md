
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultCostProvider.java

## Purpose

`DefaultCostProvider` is the baseline `CostProvider` used when no custom provider is configured. It gives every completed RPC the same scheduler cost.

## Important APIs, types, and functions

`init(String, Configuration)` is a no-op. `getCost(ProcessingDetails)` always returns `1`, ignoring the passed timing details.

## Control flow

`DecayRpcScheduler.parseCostProvider()` instantiates this class when configuration provides no `CostProvider`. Every `addResponseTime()` call then increments caller cost by one.

## State and persistence behavior

The class is stateless and persists nothing.

## Dependencies and integration points

It implements `CostProvider` and depends only on Hadoop `Configuration` and `ProcessingDetails`. It is the compatibility path for count-based scheduling rather than time-weighted scheduling.

## Risks and test signals

The main risk is semantic: expensive RPCs and cheap RPCs are treated equally. Tests should assert the no-op initialization contract and constant cost, and scheduler tests should include both default and custom provider paths.

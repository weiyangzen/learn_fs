# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CostProvider.java

## Purpose
Defines the pluggable cost calculation contract used by `DecayRpcScheduler` to account for RPC operation cost.

## Important APIs, Types, And Functions
The interface has `init(String namespace, Configuration conf)` and `getCost(ProcessingDetails details)`.

## Control Flow
Implementations initialize themselves from namespaced configuration, then compute a long cost from `ProcessingDetails` for each RPC.

## State And Persistence
The interface owns no state. Implementations may hold configuration-derived weights in memory; scheduler accounting uses returned costs.

## Dependencies And Integration Points
Configured through Hadoop `CommonConfigurationKeys.IPC_COST_PROVIDER_KEY` and consumed by `DecayRpcScheduler`. Depends on `ProcessingDetails` timing/cost metadata.

## Risks
Bad implementations can return negative, zero, or excessively large costs and distort scheduling fairness. Namespace parsing must match server IPC config keys.

## Test Signals
Tests should cover default and weighted providers, namespaced config loading, edge-case `ProcessingDetails`, and scheduler priority changes driven by computed cost.

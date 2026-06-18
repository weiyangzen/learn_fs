# sources/object-store/minio/cmd/rebalancemetric_string.go

## Purpose
This generated file provides string names for the `rebalanceMetric` enum declared in rebalance implementation code.

## Important APIs, Types, and Functions
Compile-time index checks detect enum drift. `_rebalanceMetric_name` and `_rebalanceMetric_index` encode names, and `func (i rebalanceMetric) String() string` returns known names or `rebalanceMetric(<n>)`.

## Control Flow and State
There is no mutable state or branching beyond bounds checking in `String`.

## Dependencies and Integration Points
Rebalance metrics and logs use these names for operations such as `RebalanceBuckets`, `RebalanceObject`, `RebalanceRemoveObject`, and `SaveMetadata`.

## Risks and Test Signals
The main risk is stale generated output after enum changes; normal compilation catches ordinal changes through the generated check block.

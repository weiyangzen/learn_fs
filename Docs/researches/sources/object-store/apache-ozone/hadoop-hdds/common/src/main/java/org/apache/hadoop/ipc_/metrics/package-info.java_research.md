# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/package-info.java

## Purpose
This package descriptor documents that `org.apache.hadoop.ipc_.metrics` contains RPC-related metrics.

## Important APIs, types, and functions
It declares the package and carries package-level documentation only. There are no runtime APIs.

## Control flow
No executable control flow exists.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Javadoc and package scanners can use this descriptor. Runtime integration comes from classes in the package, especially `RpcMetrics` and `RpcDetailedMetrics`.

## Risks and edge cases
The descriptor is low risk. Its main maintenance risk is stale package documentation if metrics responsibilities expand.

## Test signals
No direct unit tests are needed; compilation and Javadoc/package checks cover it.

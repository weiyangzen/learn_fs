# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BadDataLocationException.java

## Purpose
`BadDataLocationException` is an `IOException` that carries one or more failed datanode locations and a failed EC location index. It lets EC read code report which replica/index failed so callers can retry with spare locations or fail over to reconstruction.

## Important APIs and Types
Constructors accept a message, a `DatanodeDetails`, a failed index, a cause, or a list of failed locations. Accessors are `getFailedLocations()`, `addFailedLocations(List<DatanodeDetails>)`, and `getFailedLocationIndex()`.

## Control Flow
`ECBlockInputStream` throws this when a direct internal block stream fails. `ECBlockInputStreamProxy` catches it, records failed datanodes, and creates a reconstruction reader if direct EC reading cannot continue.

## State and Persistence Behavior
State is an in-memory mutable list of `DatanodeDetails` and an integer index. No persistence occurs.

## Dependencies and Integration Points
Used by EC read classes in `org.apache.hadoop.ozone.client.io`. It depends on `DatanodeDetails` and standard `IOException`.

## Risks
`getFailedLocations()` returns the mutable internal list, so callers can mutate exception state. The default `failedLocationIndex` is zero, which is meaningful for EC; callers should only consult it for constructors that set it intentionally.

## Test Signals
`TestECBlockInputStream`, `TestECBlockInputStreamProxy`, and reconstructed EC tests exercise propagation of failed locations and failover behavior.

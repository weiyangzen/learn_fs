# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneRuntime.java

## Purpose
Interface defining lifecycle and endpoint contract for a local Ozone cluster runtime.

## Important APIs, types, and functions
Extends `AutoCloseable`. Methods include `start`, `getDisplayHost`, `getScmPort`, `getOmPort`, `getS3gPort`, `getS3Endpoint`, and `close`.

## Control flow
Implementations must start services before endpoint accessors return usable values and must release resources in `close`.

## State and persistence behavior
The interface does not own state. Implementations may create persistent or ephemeral local cluster data depending on `LocalOzoneClusterConfig`.

## Dependencies and integration points
Defines the seam between CLI configuration resolution and a concrete local Ozone service launcher.

## Risks and edge cases
No implementation is present in this subset, so startup readiness, cleanup, and endpoint consistency depend on external implementers.

## Test signals
No direct tests in this subset; compile-time implementability is the signal.

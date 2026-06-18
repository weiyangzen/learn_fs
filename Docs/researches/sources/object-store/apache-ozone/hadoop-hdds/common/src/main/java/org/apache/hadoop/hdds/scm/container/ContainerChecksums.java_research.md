# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerChecksums.java

## Purpose
Immutable wrapper for container data and metadata checksums. It gives SCM/client code a typed value for checksum comparison and display, with zero meaning unknown/unset.

## Important APIs, Types, And Functions
Factories are `unknown()`, `of(long dataChecksum)`, and `of(long dataChecksum, long metadataChecksum)`. Getters expose both checksum values. `equals`, `hashCode`, and `toString` support map/set use and hex rendering.

## Control Flow
There is no complex flow; callers create values from reported checksums and compare or render them.

## State And Persistence
Instances are immutable. The singleton `UNKNOWN` avoids repeated zero/zero allocations. Persistence is external if checksums are stored in metadata or reports.

## Dependencies And Integration Points
Depends only on Java `Objects`. Integrated by container replica/report surfaces that need checksum identity.

## Risks And Test Signals
No validation distinguishes an actual zero checksum from unknown. Tests should cover equality, unknown singleton, hex `toString`, and JSON/API serialization where used.

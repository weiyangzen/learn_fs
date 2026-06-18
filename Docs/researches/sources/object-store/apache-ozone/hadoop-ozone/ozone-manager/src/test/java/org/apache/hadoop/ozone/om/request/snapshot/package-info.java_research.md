# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/snapshot/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.request.snapshot` as containing snapshot request tests. It carries JavaDoc only.

## Important APIs and Types
The only declared API is the package itself. The package groups tests for create, delete, rename, purge, set-property, and move-table-key snapshot request behavior.

## Control Flow, State, and Persistence
There is no executable control flow or state. Persistence behavior is absent in this descriptor; persistence is covered by the package's test classes.

## Dependencies and Integration Points
The file depends only on the Java package declaration and JavaDoc tooling. Its integration role is source organization for snapshot request test classes.

## Risks and Test Signals
Risk is documentation drift if new tests expand beyond snapshot request handling. Compile success is the only direct signal.

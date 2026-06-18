<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java

## Purpose
This descriptor marks raw coder utility classes as private unstable Ozone internals.

## Important APIs, Types, and Functions
No runtime API; package annotations are `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control Flow
No runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It imports HDDS annotations and applies to `CodecUtil`, `GF256`, `GaloisField`, `RSUtil`, and dump utilities.

## Risks and Test Signals
Risk is package contract drift. Build/package annotation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java -->

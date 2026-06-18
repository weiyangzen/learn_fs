<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java

## Purpose
This package descriptor documents the raw coder layer as the low-level math engine below higher-level erasure coders.

## Important APIs, Types, and Functions
It has no executable API and applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control Flow
There is no runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It imports HDDS annotations and marks all raw coder APIs as internal/unstable.

## Risks and Test Signals
Risk is compatibility contract drift. Build/package annotation checks are enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java

## Purpose
Defines the set of Ozone filesystem storage statistic counters and their Hadoop-visible symbols.

## Important APIs, types, and functions
Enum entries cover object operations (`objects_created`, `objects_read`, etc.) and filesystem method invocations (`op_create`, `op_open`, `op_recover_file`, `op_set_safe_mode`, and others). `fromSymbol` maps strings to enum values, while `getSymbol`, `getDescription`, and `toString` expose metadata.

## Control flow
A static map is populated at class load from all enum values. Lookups are constant-time and return null for unknown symbols.

## State and persistence behavior
The enum and symbol map are static immutable process state. Counts live in `OzoneFSStorageStatistics`, not here.

## Dependencies and integration points
Symbols reuse Hadoop `StorageStatistics.CommonStatisticNames` where available and add Ozone-specific names for object and lease/safe-mode operations. Filesystem and adapter classes increment these values.

## Risks and test signals
Changing symbols is an external compatibility break for monitoring and tests. New filesystem methods should add counters consistently. Tests should validate `fromSymbol`, uniqueness of symbols, descriptions, and stats increments for new enum values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java -->

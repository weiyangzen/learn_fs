<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java

## Purpose

Documents the managed RocksDB wrapper package and its rule that RocksDB native resources should be wrapped and closed through managed classes to avoid leaks.

## Important APIs, types, and functions

Package declaration: `contains RocksObject decorators and utilities to catch track RocksObject's
 * lifecycle to ensure they're properly closed before being GCed.
 */
package org.apache.hadoop.hdds.utils.db.managed`. This file provides package-level documentation and has no executable methods.

## Control flow

No runtime control flow exists. Javadoc/package metadata is consumed by documentation and compiler tooling.

## State and persistence behavior

No state is stored or persisted.

## Dependencies and integration points

The package groups related Java classes for HDDS RocksDB wrappers or native JNI support and affects generated Javadoc/package annotations.

## Risks and edge cases

The risk is documentation drift: package-level guidance must stay aligned with actual resource ownership rules in the wrapper classes.

## Test signals

Compile/Javadoc generation and consistency with nearby wrapper tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java -->

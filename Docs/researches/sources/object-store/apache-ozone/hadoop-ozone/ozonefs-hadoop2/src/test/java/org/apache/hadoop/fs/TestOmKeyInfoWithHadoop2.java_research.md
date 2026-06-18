<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java

## Purpose
Hadoop 2 classpath smoke test for `OmKeyInfo` behavior and protobuf conversion.

## Important APIs, types, and functions
The package-private class extends `org.apache.hadoop.ozone.om.helpers.TestOmKeyInfo` without adding methods, causing the inherited test suite to run under the Hadoop 2 filesystem module.

## Control flow
JUnit discovers inherited tests from the superclass.

## State and persistence behavior
State behavior is defined by the inherited OM key info tests. This file adds no state.

## Dependencies and integration points
Validates that Ozone OM helper tests still pass when Hadoop 2 compatibility dependencies and shading are on the classpath.

## Risks and test signals
The signal is classpath compatibility rather than new behavior. Failures usually indicate dependency relocation, protobuf, or Hadoop 2 API incompatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java -->

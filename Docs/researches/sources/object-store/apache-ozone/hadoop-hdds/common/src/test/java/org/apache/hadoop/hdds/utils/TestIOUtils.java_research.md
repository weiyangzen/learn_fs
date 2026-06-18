# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestIOUtils.java

## Purpose
Tests null-safe close behavior in HDDS `IOUtils`.

## Important APIs, types, and functions
- Uses `IOUtils.closeQuietly` with a null closeable and a `ByteArrayOutputStream` import context.
- Test case is `closeQuietlyNull`.

## Control flow
The test calls the close helper with null and expects no exception.

## State and persistence behavior
No meaningful state or persistence; the focus is defensive close behavior.

## Dependencies and integration points
Close helpers are used broadly in IO cleanup paths where nulls may occur after failed initialization.

## Risks and test signals
A null-unsafe close helper can turn cleanup paths into secondary failures. This test signals null tolerance.

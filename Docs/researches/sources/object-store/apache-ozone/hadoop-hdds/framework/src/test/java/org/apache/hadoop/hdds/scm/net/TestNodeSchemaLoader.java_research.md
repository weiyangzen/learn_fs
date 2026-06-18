# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaLoader.java

## Purpose

This class tests XML network topology schema loading, including valid schemas, missing files, invalid topology definitions, malformed references, unsupported types, invalid versions, and XXE protection.

## Important APIs, Types, And Functions

It uses `NodeSchemaLoader.getInstance().loadSchemaFromFile`, parameterized `getSchemaFiles`, `getClassloaderResourcePath`, and `assertMessageContains`.

## Control Flow

Parameterized tests map fixture filenames to expected error substrings, load each fixture from `networkTopologyTestFiles`, and assert `IllegalArgumentException`. Separate tests load `good.xml` successfully and require `FileNotFoundException` for a derived missing filename.

## State And Persistence

No mutable state is persisted. Test inputs are classpath XML resources.

## Dependencies And Integration Points

The tests integrate with XML schema fixtures, JUnit parameterization, classloader resource resolution, and topology schema parsing used by SCM network placement.

## Risks

Assertions depend on specific error-message substrings. The external-entity case is a security regression guard and should remain explicit if XML parser internals change.

## Test Signals

Signals include successful parse for `good.xml`, expected failures for every invalid fixture, missing-file exception, and rejection of external entity declarations.

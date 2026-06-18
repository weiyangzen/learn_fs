# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServerException.java

## Purpose
`ServerException` is the typed exception for `Server` lifecycle, configuration, service-loading, and servlet authority failures.

## Important APIs, types, and functions
The nested `ERROR` enum defines codes `S01` through `S14`, covering missing directories, invalid files, classpath loading, service interface mismatches, instantiation failures, dependency failures, status-change failures, missing system properties, and initialization failures. Constructors delegate to `XException`.

## Control flow
The class has no runtime logic beyond templated exception construction.

## State and persistence behavior
State is standard exception data plus the inherited error code. No persistence occurs.

## Dependencies and integration points
`Server`, `ServerWebApp`, and `ServiceException` use these errors. Messages rely on `MessageFormat` formatting through `XException`.

## Risks and edge cases
Some templates preserve historical typos, which tests or logs may now depend on. The protected constructor allows subclasses to pass non-`ServerException.ERROR` codes.

## Test signals
Indirectly tested through initialization failures, missing properties, and service replacement paths.

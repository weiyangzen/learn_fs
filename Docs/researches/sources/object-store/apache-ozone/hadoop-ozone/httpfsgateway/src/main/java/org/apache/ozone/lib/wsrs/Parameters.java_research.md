# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Parameters.java

## Purpose
`Parameters` is the parsed request-parameter container produced by `ParametersProvider`.

## Important APIs, types, and functions
The constructor accepts a map from parameter name to a list of `Param<?>`. `get(name, klass)` returns the first value cast through the requested parameter class. `getValues(name, klass)` returns all non-null values for repeated parameters.

## Control flow
Lookup is name-based. Missing or empty parameter lists return null or an empty list.

## State and persistence behavior
State is the parsed parameter map for one request. No persistence occurs.

## Dependencies and integration points
HttpFS REST resources use this class to retrieve typed query parameter values after provider parsing.

## Risks and edge cases
The `klass` argument is not actively checked against stored instances beyond unchecked casts. Supplying the wrong class can cause runtime `ClassCastException`.

## Test signals
REST operation tests would verify required/default/multi-value parameter behavior.

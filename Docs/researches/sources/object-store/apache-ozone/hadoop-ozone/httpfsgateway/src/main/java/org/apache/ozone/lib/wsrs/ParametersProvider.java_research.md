# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ParametersProvider.java

## Purpose
`ParametersProvider` parses servlet request query parameters according to an operation-specific parameter definition map.

## Important APIs, types, and functions
The constructor receives the driver parameter name, enum class for operations, and a map from operation enum to parameter classes. `get(HttpServletRequest)` reads the driver parameter, resolves the enum, validates support, instantiates each expected `Param` class with a default constructor, parses all supplied values, and returns a `Parameters` container.

## Control flow
Parsing is operation-driven. For each declared parameter, absent values produce one default parameter instance; present repeated values produce one parsed instance per value.

## State and persistence behavior
Provider state is immutable definition data. Request parsing creates transient maps and parameter objects.

## Dependencies and integration points
HttpFS parameter providers use it to enforce supported operations and typed query parameters before resource handlers execute.

## Risks and edge cases
`queryString.get(driverParam)[0]` can throw if the driver parameter is absent because the null check occurs after indexing. Parameter classes must have public no-arg constructors. All request parameter values are trusted as arrays from the servlet API.

## Test signals
Invalid/missing operation and bad-parameter REST tests should cover this behavior.

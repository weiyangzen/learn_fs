# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumSetParam.java

## Purpose
`EnumSetParam` parses comma-separated enum sets for request parameters.

## Important APIs, types, and functions
It extends `Param<EnumSet<E>>`, splits non-empty strings by comma, trims each token, uppercases it, and adds enum constants to an `EnumSet`. Static `toString(EnumSet)` serializes sets as comma-separated enum names. `toString()` returns `name=valueList`.

## Control flow
An empty string parses to an empty enum set rather than the default.

## State and persistence behavior
State is the inherited current enum set and enum class.

## Dependencies and integration points
Concrete WebHDFS parameters use it for options such as flag sets. `ParametersProvider` handles multi-value query parameters separately from comma-separated values.

## Risks and edge cases
Duplicate enum tokens collapse naturally in the set. Invalid tokens fail the entire parse. Serialized order follows enum declaration order.

## Test signals
No direct tests in this subset; operation parameter parsing would expose failures.

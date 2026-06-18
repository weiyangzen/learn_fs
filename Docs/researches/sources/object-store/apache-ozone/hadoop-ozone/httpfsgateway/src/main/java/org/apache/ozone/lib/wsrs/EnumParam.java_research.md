# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumParam.java

## Purpose
`EnumParam` is a typed parameter base for single enum-valued request parameters.

## Important APIs, types, and functions
It stores the enum class, uppercases input with Hadoop `StringUtils`, resolves via `Enum.valueOf`, and formats the allowed domain as comma-joined enum constants.

## Control flow
Parsing is case-insensitive for ASCII-style enum names because input is uppercased before lookup.

## State and persistence behavior
State is the inherited value and the enum class reference.

## Dependencies and integration points
Used by concrete HttpFS parameter classes and `ParametersProvider`.

## Risks and edge cases
Enum names must match uppercased input exactly. Locale/format expectations are inherited from Hadoop `StringUtils.toUpperCase`.

## Test signals
Parameter-provider tests and WebHDFS operation parsing exercise this behavior indirectly.

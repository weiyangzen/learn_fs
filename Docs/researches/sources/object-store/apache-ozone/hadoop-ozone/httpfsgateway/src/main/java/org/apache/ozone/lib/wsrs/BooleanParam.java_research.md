# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/BooleanParam.java

## Purpose
`BooleanParam` is a typed JAX-RS query parameter base for boolean values.

## Important APIs, types, and functions
It extends `Param<Boolean>`, parses case-insensitive `"true"` and `"false"`, and reports its domain as `"a boolean"`.

## Control flow
Invalid non-boolean strings throw `IllegalArgumentException`, which `Param.parseParam` wraps into a parameter-specific error message.

## State and persistence behavior
State is the inherited current value and parameter name.

## Dependencies and integration points
Concrete HttpFS parameter classes subclass it and are instantiated by `ParametersProvider`.

## Risks and edge cases
Only literal true/false values are accepted; numeric or yes/no aliases are rejected.

## Test signals
No direct tests here; request parameter parsing tests would verify invalid input mapping.

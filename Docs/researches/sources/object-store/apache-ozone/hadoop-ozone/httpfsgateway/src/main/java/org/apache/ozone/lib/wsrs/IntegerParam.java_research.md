# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/IntegerParam.java

## Purpose
`IntegerParam` is a typed request parameter base for integer values.

## Important APIs, types, and functions
It extends `Param<Integer>`, parses with `Integer.parseInt`, and reports its domain as `"an integer"`.

## Control flow
Parsing errors propagate to `Param.parseParam` and become parameter-specific `IllegalArgumentException`s.

## State and persistence behavior
State is inherited parameter name and value.

## Dependencies and integration points
Concrete HttpFS parameter classes use it for numeric query parameters.

## Risks and edge cases
Only base-10 signed Java integer syntax is accepted. Overflow is rejected by `Integer.parseInt`.

## Test signals
No direct tests in this subset.

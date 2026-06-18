# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/LongParam.java

## Purpose
`LongParam` is a typed parameter base for long integer values.

## Important APIs, types, and functions
It extends `Param<Long>`, parses with `Long.parseLong`, and reports its domain as `"a long"`.

## Control flow
Invalid or overflowing values are converted to parameter-specific `IllegalArgumentException`s by `Param`.

## State and persistence behavior
State is inherited parameter name and value.

## Dependencies and integration points
Concrete HttpFS parameters use it for lengths, offsets, block sizes, or timestamps.

## Risks and edge cases
Only signed base-10 Java long syntax is accepted.

## Test signals
No direct tests in this subset.

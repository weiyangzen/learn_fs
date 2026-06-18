# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ShortParam.java

## Purpose
`ShortParam` is a typed parameter base for short integer values, with optional radix support.

## Important APIs, types, and functions
Constructors accept parameter name, default value, and optional radix defaulting to 10. `parse` uses `Short.parseShort(str, radix)`. `getDomain()` returns `"a short"`.

## Control flow
Invalid syntax or overflow is handled by the base `Param` error wrapper.

## State and persistence behavior
State includes inherited name/value and the configured radix.

## Dependencies and integration points
Concrete permission-like or short-valued HttpFS parameters can use it.

## Risks and edge cases
Domain text does not mention non-decimal radix, so error messages may be vague for octal/hex subclasses.

## Test signals
No direct tests in this subset.

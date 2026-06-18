# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/StringParam.java

## Purpose
`StringParam` is a typed parameter base for string values, optionally constrained by a regex pattern.

## Important APIs, types, and functions
Constructors accept name, default value, and optional `Pattern`. The pattern constructor calls `parseParam(defaultValue)` to validate/default-normalize. `parseParam` trims non-null input and parses only non-empty strings. `parse` enforces the pattern when present and returns the string. `getDomain()` returns either `"a string"` or the regex.

## Control flow
Unlike base `Param`, this parser treats empty and null strings as "keep current value" after trimming.

## State and persistence behavior
State is inherited name/value plus the optional compiled pattern.

## Dependencies and integration points
Concrete HttpFS path/user/query parameters subclass it.

## Risks and edge cases
Default values are validated at construction. Whitespace is trimmed, so significant leading/trailing spaces cannot be represented.

## Test signals
REST parameter parsing tests would cover regex failures and default handling.

# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Param.java

## Purpose
`Param<T>` is the generic base class for typed JAX-RS query parameters in HttpFS.

## Important APIs, types, and functions
It stores the query parameter name and current value. `parseParam(str)` parses only non-blank input using subclass `parse`, keeps the existing default for blank input, and formats invalid-value errors with `getDomain()`. `value()` returns the parsed/default value.

## Control flow
Subclasses define both domain text and parsing. The base parser catches any exception and throws a new `IllegalArgumentException`.

## State and persistence behavior
Each parameter instance is mutable: parsing updates `value`. No persistence occurs.

## Dependencies and integration points
`ParametersProvider` instantiates concrete `Param` classes per request and stores them in `Parameters`.

## Risks and edge cases
Mutable parameter instances require fresh objects for multi-value parameters; `ParametersProvider` explicitly creates a new one after each parsed value. Blank values keep defaults, which may differ from explicit empty semantics in subclasses such as `StringParam`.

## Test signals
Parameter parsing tests and WebHDFS request validation are the main signals.

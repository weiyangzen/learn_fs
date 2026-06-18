# sources/storage-engines/foundationdb/fdbclient/vexillographer/vexillographer.cs

## Purpose
This is the original C# option-code generator driver. It parses FoundationDB option XML and dispatches to a language-specific `BindingWriter` implementation for C, C++, Java, Ruby, or Python.

## Important APIs, Types, And Functions
It defines `Scope`, `ParamType`, `Option`, `BindingWriter`, and static class `vexillographer`. Important methods are `Main`, `usage`, `parseOptions`, `Scope.getDescription`, `AttributeOrNull`, and `AttributeNonNull`. `Option` exposes `isDeprecated()` and `getParameterComment()`.

## Control Flow
`Main` validates at least three arguments, parses options from XML using the requested binding name, loads `vexillographer.<binding>` by reflection, constructs it, and invokes `writeFiles`. `parseOptions` walks `<Options>/<Scope>/<Option>`, parses enum values and flags, honors comma-separated `disableOn` entries for the selected binding, and returns a list of `Option` objects.

## State And Persistence Behavior
The driver stores parsed option definitions in memory and delegates all file persistence to the selected writer. It has no durable state of its own.

## Dependencies And Integration Points
It depends on LINQ-to-XML and the sibling language writer classes. The generated artifacts are part of FoundationDB binding build pipelines and must stay consistent across languages.

## Risks And Edge Cases
Most parse exceptions are swallowed into return code `1`, reducing diagnostic detail. Reflection failures print stack traces and return `31`. XML attributes are assumed present for scope names, option names, and codes; missing required data aborts generation. Binding names must match class names exactly.

## Test Signals
Driver tests should cover successful generation for each binding, `disableOn` filtering, missing required attributes, unknown binding names, deprecated comments, hidden/persistent/sensitive flags, and scope-description mappings.

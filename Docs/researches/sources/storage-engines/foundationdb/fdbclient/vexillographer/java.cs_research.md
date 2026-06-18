# sources/storage-engines/foundationdb/fdbclient/vexillographer/java.cs

## Purpose
This C# binding writer generates Java option classes, enums, and `FDBException` predicate helpers from the shared FoundationDB option XML.

## Important APIs, Types, And Functions
Key helpers are `formatComment`, `replaceTicks`, `getEnum`, `toCamelCase`, `toSetFuncName`, `toPredicateFuncName`, `getJavaTypeName`, `writeOptionsClass`, `writePredicateClass`, `writeEnumClass`, and `writeFiles`. `scopeDocOptions` controls public visibility and whether a scope becomes a settable options class or enum.

## Control Flow
For each `Scope`, `writeFiles` chooses an output Java file: settable option scopes get `<Scope>s.java`, `ErrorPredicate` gets `FDBException.java`, and non-settable scopes get enum files. Hidden options are skipped. Comments are converted to Javadoc, double-backtick spans become `{@code ...}`, deprecated comments add `@Deprecated`, and parameterized options get typed setter methods.

## State And Persistence Behavior
The writer creates multiple Java files in an existing output directory. Runtime state in generated classes is minimal: option code constants and methods that call `setOption` or `FDB.evalErrorPredicate`.

## Dependencies And Integration Points
Generated output targets package `com.apple.foundationdb` and integrates with Java binding classes such as `OptionsSet`, `OptionConsumer`, `Transaction`, `Database`, and `FDBException`. It depends on option metadata parsed by `vexillographer.cs`.

## Risks And Edge Cases
`replaceTicks` throws on unmatched double ticks, so documentation formatting can fail generation. Output newline is set to `"\r"`, which is unusual and may affect diff/test expectations. Java string/comment escaping is limited; problematic XML descriptions can break Javadoc or source.

## Test Signals
Tests should compile generated Java, verify hidden options are absent, deprecated options are annotated, error predicates call the right native codes, and malformed double-tick comments fail generation predictably.

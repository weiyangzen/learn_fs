# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBOptions.h

Purpose: Provides generic option metadata and ordered unique option storage used by generated database/transaction option tables and default-option handling.

Important APIs/types/functions: `FDBOptionInfo` stores name, comment, parameter comment, parameter presence, hidden/persistent/sensitive flags, default target option code, and parameter type (`None`, `String`, `Int`, `Bytes`). `FDBOptionInfoMap<T>` wraps a map from `T::Option` to metadata and invokes `T::init()` in its constructor. `UniqueOrderedOptionList<T>` stores each option at most once while preserving the most recent insertion order and value. `ADD_OPTION_INFO` inserts metadata into a type's static option map.

Control flow: Generated option classes initialize their metadata through `ADD_OPTION_INFO`. Callers look up metadata with `getMustExist()` and store default options with `UniqueOrderedOptionList::addOption()`, which removes older entries before appending the latest value.

State and persistence behavior: Option metadata is static/in-memory. Unique ordered option lists are runtime state, but options marked persistent in metadata may affect durable option handling elsewhere. Sensitive flags guide redaction/display decisions.

Dependencies and integration points: Depends on `flow/Arena.h` for `Optional<Standalone<StringRef>>`. Used by generated `FDBOptions.g.h`, NativeAPI option parsing, transaction default options in `DatabaseContext`, fdbcli/help surfaces, and bindings.

Risks: `T::init()` in the map constructor depends on generated static initialization patterns. Incorrect metadata can expose hidden/sensitive options or misparse parameter types. `defaultFor` semantics replace prior default values, so duplicate handling must remain unique and ordered.

Test signals: Generated option metadata initialization; lookup assertions for every generated option; duplicate option insertion order; parameter type validation; hidden/sensitive display filtering; database transaction default option application.

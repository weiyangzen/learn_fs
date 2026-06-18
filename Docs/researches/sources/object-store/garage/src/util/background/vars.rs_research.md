<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/vars.rs -->
# sources/object-store/garage/src/util/background/vars.rs

## Purpose
Dynamic background variable registry for exposing and updating persisted runtime tuning values through a uniform string interface.

## Important APIs, types, and functions
`BgVars` stores named boxed `BgVarTrait` objects. `register_rw` registers a read/write variable from a `PersisterShared<V>` plus typed getter/setter closures; `register_ro` installs a read-only value; `get`, `get_all`, and `set` provide string access.

## Control flow
Registration clones the shared persister into closures. Reads call the typed getter and stringify the result. Writes parse the incoming string into `T`, call the setter, and propagate conversion or persistence errors.

## State and persistence behavior
The registry is in-memory, but registered setters can mutate and save `PersisterShared` values, so CLI/admin updates can become durable. Missing names and read-only writes are surfaced as `Error::Message`.

## Dependencies and integration points
Depends on Garage error helpers, migration-aware persisters, `FromStr`/`ToString`, and background/admin code that exposes worker tuning variables.

## Risks and test signals
String parsing is deliberately generic; ambiguous display/parse formats can make values non-round-trippable. Tests should cover unknown variable errors, read-only rejection, parse errors, and persistence side effects from setters.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/vars.rs -->

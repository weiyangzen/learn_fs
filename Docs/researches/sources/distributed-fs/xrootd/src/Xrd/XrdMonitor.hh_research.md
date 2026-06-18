## sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.hh

Purpose: declares the monitor registry and formatter that backs `XrdMonRoll` summary statistics.

Important APIs/types/functions: `Mopts` combines format and set filters: `F_JSON`, `X_PLUG`, and `X_ADON`. Public `Format()` overloads format by cursor or set name. `Register()` accepts a roll type, set name, item array, and item count. Private `RegInfo` stores headers, template, type, count, and item vector pointer. Private helpers validate and format values.

Control flow: `XrdMonRoll` calls `Register()`, then the report machinery calls `Format()` to serialize selected sets in JSON or XML form.

State/persistence: `regVec` holds registered sets for the life of the monitor. `Registered()` reports whether any set has been registered.

Dependencies/integration: includes `XrdMonRoll.hh` and standard containers. It is not internally synchronized around `regVec`, implying registration should occur during configuration before concurrent reporting.

Risks: lack of registry locking makes concurrent register/format unsafe. `RegInfo` destructor frees metadata but not item storage, so ownership must remain external. Output format flags are bit masks; passing `F_JSON` without `X_PLUG` or `X_ADON` will skip all sets in cursor formatting.

Test signals: compile tests for option combinations, registration lifetime, cursor advancement across filtered sets, and named-set lookup across plugin/addon categories.

## sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.hh

Purpose: defines the public API for registering addon/plugin counter sets that are included in summary statistics emitted by `xrootd.report`.

Important APIs/types/functions: nested `Item` represents numeric, text, mutex, or schema tokens. `Schema` marks array/object begin and end. `Family` and `Trait` classify values for `XrdMonitor`. Constructors accept float, double, char text, string, schema, mutex lock/unlock markers, native `RAtomic` values, and bit-width `RAtomic` values. `rollType` maps deprecated `Misc`/`Protocol` to `AddOn`/`Plugin`. `Register()` overloads support modern `std::vector<Item>` and deprecated `setMember` arrays.

Control flow: a component defines an item list describing JSON/XML shape and variable references, then registers it through an `XrdMonRoll` instance. `XrdMonitor` later validates and formats the list.

State/persistence: item objects hold pointers or references to live variables; the item vector must outlive monitoring. `EOV` is the sentinel for legacy arrays. No data is persisted beyond process memory.

Dependencies/integration: depends on `XrdSysRAtomic` and `XrdMonitor`.

Risks: pointer lifetime is the main hazard. Text values are emitted without escaping in the formatter, so arbitrary strings containing JSON/XML metacharacters can produce invalid output. Mutex items allow monitor formatting to lock component state, but incorrect lock/unlock ordering is rejected only at registration validation.

Test signals: validate nested arrays/objects, mutex lock pairs, all atomic variants, text/string output, deprecated registration, duplicate set rejection, and XML tag defaults for array items.

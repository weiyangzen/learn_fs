## sources/distributed-fs/xrootd/src/Xrd/XrdMonitor.cc

Purpose: validates registered monitor roll-up descriptions and formats registered addon/plugin counter sets as JSON or XML.

Important APIs/types/functions: `RegInfo` stores set metadata, headers, templates, and item pointers. `Register()` maps roll types, rejects bad/duplicate sets, validates item syntax, builds JSON/XML headers, and stores the registry. `Format()` emits by index or set name. `FormJSON()` and `FormXML()` walk item vectors, handling schema and mutex items. `V2S()` formats atomics/floats/doubles, `V2T()` formats text, and `Validate()` checks keys, schema nesting, and mutex lock pairing.

Control flow: registration happens during component initialization. Reporting calls `Format()` repeatedly with an item cursor or a named set; only sets matching requested plugin/addon flags are emitted. Formatting directly reads the registered variable pointers.

State/persistence: `regVec` owns `RegInfo` objects for process lifetime. Each `RegInfo` references item vectors owned externally or intentionally leaked by legacy conversion.

Dependencies/integration: uses global `XrdSysError Log`, `XrdSysMutex`, standard containers, and `XrdMonRoll::Item`.

Risks: `Register()` assigns `regInfo->eTmplt = strdup(buff)` before `buff` is initialized for that purpose and leaks the constructor-created template; this likely corrupts later validation messages after successful registration. JSON/XML text is not escaped. `FormJSON()` resets comma anchor inside nested containers in a simplistic way; complex nested schemas need coverage. Formatting can deadlock if registered mutex items conflict with locks held by the reporting path.

Test signals: unit tests should cover invalid schemas, unbalanced mutex markers, duplicate sets, named and cursor formatting, buffer-too-small returns, text escaping expectations, and nested JSON/XML arrays and objects.

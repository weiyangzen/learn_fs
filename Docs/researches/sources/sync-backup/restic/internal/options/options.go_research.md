## sources/sync-backup/restic/internal/options/options.go

Purpose: parsing, listing, namespace extraction, and reflection-based application of backend-specific `-o key=value` options.

Important APIs/types: `Options map[string]string` stores normalized options. `Register`, `List`, `appendAllOptions`, and `listOptions` support discoverable option help via struct tags. `Help` and `helpList` carry namespace/name/text and sorted ordering. `splitKeyValue` lowercases and trims keys and trims values. `Parse` accepts duplicate keys only if values match. `Extract` returns options under a namespace and strips the namespace prefix. `Apply` maps option names to struct fields tagged `option`, supporting `string`, `int`, `uint`, `bool`, and `time.Duration`.

Control flow and state: `opts` is a package-global registered option list. `Apply` reflects on a pointer to a struct and panics for duplicate tags or unsupported field types; unknown options return fatal errors with namespace-qualified names.

Dependencies and integration points: used by global backend parsing before opening/creating backends. Backend config structs must expose supported options through struct tags, and command help can list registered options.

Risks and test signals: reflection panics are possible for developer mistakes in config struct tags or unsupported types. Option parsing is intentionally permissive about missing `=` values. Tests cover parsing, duplicates, invalid keys, namespace extraction, applying typed fields, invalid conversions, listing pointer/value structs, and sorted multi-namespace help.

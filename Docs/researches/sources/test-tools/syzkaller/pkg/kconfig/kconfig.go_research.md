## sources/test-tools/syzkaller/pkg/kconfig/kconfig.go

Purpose: parses Linux Kconfig files, include trees, menus, config entries, dependency/select relationships, and exposes dependency queries for minimization.

Important APIs/types/functions: `KConfig`, `Menu`, `MenuKind`, `ConfigType`, `Menu.DependsOn`, `Menu.Prompt`, `Parse`, `ParseData`, parser methods `parseFile`, `parseLine`, `parseMenu`, `parseConfigType`, `parseProperty`, `includeSource`, stack helpers, `tryParsePrompt`, `parseDefaultValue`, and `expandString`.

Control flow: parsing is line-oriented with a menu stack. `source` recursively switches parsers; menu/config constructs create or push `Menu` nodes; properties attach prompts/defaults/dependencies/selects. After parsing, `walk` propagates inherited dependencies/visibility and indexes config entries, then `setSelectedBy` builds reverse select links.

State and persistence: reads Kconfig files from disk including nested sources. Parsed `Menu` nodes cache dependency closures via `sync.Once`.

Dependencies and integration: depends on `targets.Target` for `SRCARCH` expansion, `expr.go`, and `parser.go`. Used by minimization and tests.

Risks: only a subset of Kconfig syntax is modeled. Select/imply conditions are ignored. Include expansion supports a fixed set of variables. Help indentation handling is delicate. `mainmenu` is represented as `MenuConfig` with empty name.

Test signals: `kconfig_test.go` covers parsing, dependency/select queries, and fuzz entry point.

## sources/test-tools/syzkaller/pkg/kconfig/config.go

Purpose: parses, edits, clones, and serializes Linux `.config` files.

Important APIs/types/functions: `ConfigFile`, `Config`, constants `Yes`, `Mod`, `No`, `Value`, `Set`, `Unset`, `ModToYes`, `ModToNo`, `Serialize`, `ParseConfig`, `ParseConfigData`, `Clone`, and `parseLine`.

Control flow: parsing scans line-by-line, matching enabled/value lines and `# CONFIG_X is not set` lines via regex; other lines are preserved as comments attached to future configs or trailing comments. Serialization re-emits comments and config assignments with `CONFIG_` prefix.

State and persistence: reads `.config` files and returns mutable in-memory config lists/maps; serialization produces bytes for callers to persist.

Dependencies and integration: used by Kconfig minimization and kernel build/test tooling. Public APIs intentionally omit `CONFIG_` prefixes.

Risks: regex only accepts a subset of valid config values. Duplicate config lines collapse in `Map` but all entries remain in `Configs` behavior depends on parsing order. `No` uses a sentinel string that callers should not write directly.

Test signals: minimization and Kconfig tests exercise config parsing indirectly; no dedicated config test in this subset.

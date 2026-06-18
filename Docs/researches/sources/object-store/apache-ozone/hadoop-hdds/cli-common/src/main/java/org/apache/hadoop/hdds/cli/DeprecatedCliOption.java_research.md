# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DeprecatedCliOption.java

Purpose: Emits compatibility warnings when legacy multi-character single-dash CLI options are used.

Important APIs/types/functions: `DEPRECATED_OPTIONS` is a `LinkedHashMap` mapping old names such as `-conf`, `-id`, `-host`, and `-pt` to preferred long options. `warnIfMatched(CommandLine.ParseResult)` scans a root parse result and subcommand parse results. `warn(PrintWriter, String, String)` formats the warning.

Control flow: `GenericCli` installs an execution strategy that calls `warnIfMatched` before `RunLast`. The scanner iterates every `CommandLine` in the parse-result chain and checks `hasMatchedOption` for each deprecated name.

State and persistence behavior: Static immutable-by-convention map; no runtime persistence. Warnings are written to stderr.

Dependencies and integration points: Depends on picocli parse state and is coupled to hidden/deprecated option aliases in Ozone CLI commands.

Risks: The map must stay synchronized with actual aliases; otherwise warnings may be absent or check names not defined on a command. It only warns for options recognized by picocli, so removed aliases will fail parsing before warning.

Test signals: CLI parsing tests should assert warnings for deprecated aliases, no warnings for preferred aliases, and behavior across nested subcommands.

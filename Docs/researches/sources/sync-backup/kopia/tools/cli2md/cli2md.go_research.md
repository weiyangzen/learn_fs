<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md.go -->
# sources/sync-backup/kopia/tools/cli2md/cli2md.go

This command generates Hugo/Markdown CLI reference pages from the Kopia kingpin app model. It defines base output directory, common/advanced sections, flag escaping, default overrides, and functions to emit flags, args, app flags, command indexes, subcommands, and pages.

Control flow in `main` parses flags, verifies base dir, removes existing generated common/advanced sections, obtains the CLI model, generates global flags, and recursively flattens commands. `flattenChildren` carries parent flags into descendants and can force hidden status. `generateSubcommandPage` writes front matter, synopsis, usage, flags, args, examples/details, and subcommand listings. `escapeFlags` protects CLI flags from Markdown interpretation.

State is generated files under `content/docs/Reference/Command-Line`. Dependencies are kingpin model internals and Kopia CLI registration. Risks include deleting the wrong base dir, generated docs drift from CLI model fields, hidden/advanced command classification, and Markdown escaping gaps. Unit tests cover flag escaping only.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md.go -->

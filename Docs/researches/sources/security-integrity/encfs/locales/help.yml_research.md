## sources/security-integrity/encfs/locales/help.yml

Purpose: i18n catalog for clap help/about text for `encfs`, `encfsctl`, and `encfsr` command-line interfaces in English, French, and German.

Important APIs and keys: `_version: 2`, `help.encfs.*` for mount flags (`foreground`, `verbose`, `debug`, `public`, `extpass`, `stdinpass`, `read_only`, permissions, root/mount point), `help.encfsctl.*` for subcommands and options, and `help.encfsr.*` for reverse mode. Control flow is data-only; CLI builders or derive annotations call these keys through rust-i18n.

State and persistence: Static localized strings. Dependencies are correct YAML, stable key names, and placeholder-free help content. Integration shapes discoverability of security-sensitive options such as `--extpass`, `--stdinpass`, `--ignore-mac`, and reverse-mode unique-IV flags. Risks are stale help when CLI flags change; because help text is localized, every semantic option change requires catalog updates in all languages.

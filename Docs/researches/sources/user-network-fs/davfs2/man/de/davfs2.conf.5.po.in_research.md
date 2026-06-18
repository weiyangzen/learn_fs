# sources/user-network-fs/davfs2/man/de/davfs2.conf.5.po.in

## Purpose
This PO input provides the German translation for the generated `davfs2.conf(5)` manpage.

## Important APIs and structure
It is gettext/po4a data with metadata headers, source references, message flags, `msgid` English source text, and `msgstr` German translations. Placeholders such as `@CONFIGFILE@`, `@PROGRAM_NAME@`, `@SYS_CONF_DIR@`, `@PACKAGE@`, and roff formatting markers must be preserved exactly. It covers syntax rules, precedence, all documented config option names/defaults, debug categories, authors, home, and see-also sections.

## Control flow
There is no runtime flow. During documentation build, po4a/gettext tooling combines this translation with generated source manpage content to produce a localized section 5 page.

## State and persistence behavior
The output is installed documentation only. It does not alter runtime config state, but incorrect translation can cause persistent misconfiguration by administrators.

## Dependencies and integration points
It is installed through `man/de/meson.build` and depends on po4a-compatible syntax. It must track `man/davfs2.conf.5.in` and generated message references.

## Risks
Header metadata is stale relative to the 2026 POT creation date: project version and revision date are older. The source includes translated warnings for security-sensitive certificate, secrets, ETag, cache, and debug behavior, so stale or inaccurate text has operational risk. Some translated text includes typos, but no fuzzy markers were found in the inspected option list.

## Test signals
Run po4a/msgfmt validation, build the German manpage, check placeholder preservation, and compare message coverage against the current POT. Review translations for changed options and security warnings after any English source update.

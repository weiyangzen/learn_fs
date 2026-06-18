<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/po4a.conf -->
# Research: sources/user-network-fs/davfs2/man/po4a.conf

Purpose: po4a configuration that manages translation extraction and generated translated manpage sources for davfs2 manuals.

Important directives: `[po4a_langs] de es`, `[po4a_paths] $master.pot $lang:$lang/$master.po`, and three `[type:man]` mappings for `davfs2.conf.5.in`, `mount.davfs.8.in`, and `umount.davfs.8.in`. German has translator addenda and UTF-8 options for all three pages. Spanish is mapped only for `davfs2.conf.5.in` with `opt_es:"-k 60 -L UTF-8"`.

Control flow and integration: `man/meson.build` runs `po4a po4a.conf` before entering language subdirs. Generated/updated language files are then consumed by language-specific Meson fragments.

State and persistence: po4a uses POT/PO files as durable translation state and may regenerate translated manpage intermediates. Translation coverage differs per language and per page.

Dependencies: requires po4a with manpage support and stable relative paths from `man/`. Addendum paths must exist for German. Encoding flags must match the PO files.

Risks: the `-k 60` Spanish threshold can produce partially translated output. Spanish coverage is limited to `davfs2.conf.5.in`; mount and umount remain untranslated for Spanish despite language being listed. Build reproducibility depends on po4a version behavior because the root Meson file requires `po4a --version`.

Test signals: run `po4a po4a.conf` from `man/`, check generated files for all listed mappings, and inspect fuzzy/untranslated thresholds in CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/po4a.conf -->

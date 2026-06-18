# sources/user-network-fs/samba/source3/locale/net/genmsg

Purpose: `locale/net/genmsg` is a shell helper for regenerating gettext `.po` files for Samba's `net` command translations.

Important logic: `add_basedir_to_filelist` prefixes each listed source file with `../../utils`. `FILES` enumerates many `net*.c` sources. `LANGS` lists supported locale directories. The script runs `xgettext` with domain `net`, comment extraction, `_` and `N_` keywords, and width 256, then iterates languages, preserving existing translations through `msgmerge` from each old language file into the new `net.po` template.

Control flow and state: the script creates or touches each `${lang}.po`, renames it to `${lang}.po.old`, merges, writes the new `${lang}.po`, removes the old temporary, and deletes the generated `net.po` template. It mutates translation files in the current directory.

Dependencies and integration: requires POSIX shell, `xgettext`, `msgmerge`, the locale directory layout, and the listed source files under `source3/utils`. It integrates with gettext translation maintenance, while `locale/wscript` handles build-time compilation/install when gettext is enabled.

Risks: running from the wrong directory will update or create files in the wrong place. The unquoted file iteration assumes no spaces in paths/language names. Missing source files or gettext tools will fail midway and may leave `.po.old` files. The source list can become stale as `net` command files are added or removed.

Test signals: run from `source3/locale/net` with gettext tools installed, verify `net.po` is removed at the end, all language `.po` files remain parseable with `msgfmt -c`, and new translatable strings from listed `net*.c` files appear in merged catalogs.

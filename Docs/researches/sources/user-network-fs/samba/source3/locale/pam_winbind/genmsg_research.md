# sources/user-network-fs/samba/source3/locale/pam_winbind/genmsg

Purpose: `locale/pam_winbind/genmsg` regenerates gettext `.po` catalogs for the `pam_winbind` component.

Important logic: `FILES` points at `../../../nsswitch/pam_winbind.c`, `../../../nsswitch/pam_winbind.h`, and `../../../libcli/util/nterr.c`. `LANGS` lists the maintained translation languages. The script ensures `pam_winbind.po` exists, runs `xgettext` with domain `pam_winbind`, `_` and `N_` keywords, and width 256, then loops over languages and uses `msgmerge` to merge the generated template into each existing language file.

Control flow and state: each language file is touched, moved to `${lang}.po.old`, merged back to `${lang}.po`, and the old file is removed. The generated `pam_winbind.po` template is removed at completion. It mutates files in the current locale directory.

Dependencies and integration: requires shell, gettext tools, source files in `nsswitch` and `libcli/util`, and locale build support. `locale/wscript` later compiles/install these catalogs when gettext is enabled.

Risks: like the `net` script, it assumes it is run from the correct directory and that paths have no spaces. Failure during `msgmerge` can leave temporary files or incomplete catalogs. Including `nterr.c` means NT error string changes affect pam_winbind translations; stale source lists can miss messages.

Test signals: run the script in `source3/locale/pam_winbind`, verify all listed language catalogs exist, validate with `msgfmt -c`, confirm `pam_winbind.po` cleanup, and inspect that changed PAM/NT-error strings are represented.

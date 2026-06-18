# sources/security-integrity/ecryptfs-utils/po/POTFILES.in

Purpose: gettext/intltool input list for translatable files.

Important APIs/data: includes desktop files, `ecryptfs-record-passphrase`, and several shell utilities such as mount/private/recover/rewrite/setup/swap/umount.

Control flow/state: gettext tooling scans these paths to generate/update translation templates.

Dependencies/integration: used by `AM_GLIB_GNU_GETTEXT` and intltool during build/dist.

Risks: missing files lead to untranslated user-facing strings; stale paths break translation updates.

Test signals: `make update-po` or distribution translation generation.

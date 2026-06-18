<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/meson.build -->
# Research: sources/user-network-fs/davfs2/man/es/meson.build

Purpose: Meson fragment for installing the Spanish translated `davfs2.conf(5)` manpage.

Important APIs: uses `configure_file(input: 'davfs2.conf.5.in.po', output: 'davfs2.conf.5', configuration: mandata, install_dir: mandir + '/es/man5')`. It consumes `mandata` from the parent `man/meson.build`, so all substitution variables are shared with the English manpages.

Control flow and integration: the parent `man/meson.build` enters this subdirectory only when `enable_nls` is true. `run_command('po4a', 'po4a.conf')` in the parent is expected to have generated or refreshed translated inputs before this configure step.

State and persistence: no local state beyond the generated configured manpage under the build directory and the installed Spanish manpage.

Dependencies: depends on parent-scope `mandata`, `mandir`, and Meson configured-file semantics. It also implicitly depends on po4a-generated Spanish material having the expected filename.

Risks: this installs only `davfs2.conf.5`; Spanish translations for `mount.davfs.8` and `umount.davfs.8` are not configured here. If the po4a output name differs from `davfs2.conf.5.in.po`, Meson configuration fails. The input extension is unusual for a configured manpage and should be checked against po4a outputs.

Test signals: configure with `-Dnls=true -Dman=true`, verify `meson install` places `davfs2.conf.5` under `$mandir/es/man5`, and confirm substituted tokens are resolved.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/meson.build -->

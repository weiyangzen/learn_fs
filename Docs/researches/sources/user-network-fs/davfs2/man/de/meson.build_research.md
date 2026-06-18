# sources/user-network-fs/davfs2/man/de/meson.build

## Purpose
This Meson fragment configures installation of German localized davfs2 manpages.

## Important APIs and targets
It uses `configure_file` three times: `davfs2.conf.5.in.po` to `davfs2.conf.5` under `man5`, `mount.davfs.8.in.po` to `mount.davfs.8` under `man8`, and `umount.davfs.8.in.po` to `umount.davfs.8` under `man8`, all with the `mandata` configuration object.

## Control flow
The file has no conditionals. Meson substitutes configured variables into each localized PO-derived manpage input and installs the outputs.

## State and persistence behavior
At install time it writes localized documentation into `${mandir}/de`. It does not affect runtime behavior.

## Dependencies and integration points
It depends on top-level `mandata` and `mandir` definitions and on the German translation input filenames matching the build tree. It integrates the localization files into packaging/install output.

## Risks
The input names in this Meson file include `.in.po`, while the researched files are named `.po.in`; if the repository does not generate or rename those intermediates elsewhere, this can break localized manpage installation. There is no validation in this fragment that translated messages are complete.

## Test signals
Run `meson setup` and `meson install --destdir`, verify German manpages are generated and installed, and inspect build logs for missing input files. Add an install test that checks all three outputs exist under the expected language directories.

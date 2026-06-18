# sources/sync-backup/casync/doc/meson.build

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/doc/meson.build -->
## sources/sync-backup/casync/doc/meson.build

Purpose: this Meson fragment builds and optionally installs casync's manual page from Sphinx documentation sources.

Important declarations: `sphinx_sources` lists `conf.py`, `casync.rst`, and `index.rst`. `man_pages` lists `casync.1`. `mandir1` resolves to `get_option('mandir')/man1`. When `get_option('man')` is true, Meson finds `sphinx-build-3` or `sphinx-build` and creates a `custom_target('man')`.

Control flow: the top-level build enters this subdir unconditionally. The actual Sphinx target is conditional on the `man` option. The custom target runs Sphinx with `-b man`, using the current source directory as input and current build directory as output, then installs the generated page into section 1.

State and persistence: generated state is limited to the Meson build directory and installed man page output. No source files are modified.

Dependencies and integration points: depends on Meson, Sphinx, the doc source files, and `doc/conf.py`. It is included by the top-level `meson.build`, and its `man` option is declared in `meson_options.txt`.

Risks: if `man=true` and Sphinx is missing, configuration fails because `find_program` is required by default. The hardcoded output list must match what Sphinx writes; source renames require updates here. The `man` option description in `meson_options.txt` appears to have a missing closing parenthesis, a cosmetic issue but useful signal for polish.

Test signals: configuring with `-Dman=true` should find Sphinx and build `casync.1`. Configuring with `-Dman=false` should skip Sphinx entirely.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/doc/meson.build -->

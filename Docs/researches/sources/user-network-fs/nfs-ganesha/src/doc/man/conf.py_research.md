<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py -->
## sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py

Purpose: Sphinx configuration that auto-discovers NFS-Ganesha man pages.

Important APIs/functions: `_get_description(fname, base)` parses each `.rst` file's initial title block, expects an underline of `=` characters, splits the title line on `--`, and asserts the page name matches the filename base. `_get_manpages()` scans the directory for `.rst` files except `index.rst` and yields Sphinx `man_pages` tuples with section 8.

Control flow/state: at import time, `man_pages = list(_get_manpages())` discovers pages dynamically. `master_doc = 'index'` is set to satisfy Sphinx toctree expectations.

Dependencies/integration: used by the CMake Sphinx command with `-c` pointing at this directory. It relies on strict heading conventions across all man `.rst` files.

Risks: import-time asserts make documentation builds fail hard on a malformed title, missing `--`, or filename/title mismatch. It discovers all `.rst` files, while CMake selects a feature-dependent subset as explicit dependencies, so generated pages and dependency tracking can diverge.

Test signals: run `sphinx-build -b man` and add a malformed temporary `.rst` to confirm failures are clear. Verify all selected feature pages have titles in `name -- description` form.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py -->

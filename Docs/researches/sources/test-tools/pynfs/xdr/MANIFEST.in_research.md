<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/xdr/MANIFEST.in -->
# sources/test-tools/pynfs/xdr/MANIFEST.in

Purpose: setuptools manifest rule for the xdrgen package.

Important declarations: the file contains `include *.py`, which requests Python files in this package directory be included in source distributions.

Control flow: no executable logic. It is consumed by setuptools during source distribution creation.

State and persistence: affects generated sdist contents only; no runtime state.

Dependencies and integration: pairs with `xdr/setup.py`, ensuring `xdrgen.py` and any same-directory Python helpers are packaged.

Risks: the rule is narrow and omits grammar tables, tests, README files, or `.x` fixtures if those are later added. Because this file has no comments or exclusions, maintainers must remember to update it when packaging non-Python assets. Test signals: run `python setup.py sdist` in `xdr` and inspect the archive contents.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/xdr/MANIFEST.in -->

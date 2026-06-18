<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/xdr/setup.py -->
# sources/test-tools/pynfs/xdr/setup.py

Purpose: package metadata for distributing `xdrgen`, pynfs' Python XDR/RPC code generator.

Important declarations: `setup(name="xdrgen", version="0.0.0", py_modules=["xdrgen"], scripts=["xdrgen.py"], ...)` exposes both an importable module and a script file. Metadata identifies the tool as generating Python code from `.x` files and records GPL licensing and maintainers.

Control flow: no custom commands; the setuptools `setup` call runs at import/execution time.

State and persistence: creates normal setuptools build/install artifacts. It does not generate XDR output by itself.

Dependencies and integration: comments mention PLY as a requirement but the `requires`/`install_requires` entry is disabled. It integrates with `rpc/setup.py`, which imports `xdrgen` directly for code generation.

Risks: placeholder version, disabled dependency declaration, and exposing `xdrgen.py` as both module and script can confuse packaging expectations. If PLY is missing, installation may succeed but runtime generation fails. Test signals: run `python3 setup.py build`, then import `xdrgen` in an isolated environment with PLY installed.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/xdr/setup.py -->

# sources/storage-engines/foundationdb/bindings/python/MANIFEST.in

Purpose: Python source distribution manifest additions.

Important APIs and flow: includes `README.rst` and `LICENSE` in the packaged sdist. It is consumed by Python build tooling invoked from the binding CMake packaging flow.

State and persistence: no runtime state; affects packaged file contents. Risks are omissions if additional non-Python runtime files become required, and duplication with packaging metadata in `pyproject.toml`. Test signal is package inspection or install tests confirming README/license presence.

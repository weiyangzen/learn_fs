# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/meson.build

This Meson file builds and tests the Python bindings when `want_python` is enabled.

Core behavior:
- Checks whether Python has `Py_NewRef`; warns if compatibility shim is needed.
- Detects SWIG version and uses `-py3` only for older SWIG.
- Generates `nvme.py` and `nvme_wrap.c` from `nvme.i`.
- Builds `_nvme` Python extension module.
- Declares `python3_libnvme_dep` with `nvme_py_path` for parent Meson fallback use.
- Copies/configures `__init__.py` and `_exceptions.py` into the build/install package directory.
- Sets test environment with `PYTHONPATH`, `MALLOC_PERTURB_`, and `PYTHONMALLOC=malloc`.
- Registers import and Python unit tests.

Tests registered:
- `create-ctrl-object`
- `sigsegv-during-gc`
- `read-nbft-file`
- `object-properties-and-errors`
- `setattr-guards`

Integration role:
- Owns SWIG-based Python module generation, installation, and binding tests.

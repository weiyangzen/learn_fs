# File Research: sources/virtualization/nvme-cli/pyproject.toml

Python packaging metadata for libnvme bindings.

Key elements:
- Uses `mesonpy` as build backend with requirements: `meson-python`, `meson`, `ninja`, and `swig`.
- Publishes project name `libnvme`, dynamic version, LGPL-2.1-or-later license text, and Python `>=3.6`.
- Declares homepage/source/bug tracker URLs pointing at linux-nvme/nvme-cli.
- Configures meson-python setup arguments to disable nvme CLI, enable libnvme and Python, enable PyPI mode, and disable tests/examples.

Role:
- Supports building Python bindings from the same source tree without building the CLI tools or test suites.

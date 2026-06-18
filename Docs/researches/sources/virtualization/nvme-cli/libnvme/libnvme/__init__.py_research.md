# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/__init__.py

This Python package initializer exposes generated version strings.

Content:
- `__version__ = @LIBNVME_VERSION@`
- `__git_version__ = @GIT_VERSION@`

Integration role:
- Processed through Meson `configure_file`.
- Installed with the SWIG-generated Python bindings.

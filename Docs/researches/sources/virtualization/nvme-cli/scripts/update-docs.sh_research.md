# File Research: sources/virtualization/nvme-cli/scripts/update-docs.sh

Documentation regeneration script.

Key elements:
- Creates a temporary Meson build directory and removes it on exit.
- Configures Meson with nvme, libnvme, all docs, and docs build enabled.
- Compiles the build.
- Replaces generated libnvme man pages, RST files, `conf.py`, `index.rst`, and config schema.
- Copies generated nvme-cli `.1` man pages and `.html` files into `Documentation/`.

Role:
- Used by release automation to refresh generated documentation artifacts.

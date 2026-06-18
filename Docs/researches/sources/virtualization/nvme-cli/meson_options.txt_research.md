# File Research: sources/virtualization/nvme-cli/meson_options.txt

This file defines configurable Meson options for nvme-cli/libnvme builds.

Feature options:
- `nvme`: build nvme executable, default enabled.
- `libnvme`: build libnvme library, default enabled.
- `fabrics`: NVMe-oF support, default enabled.
- `mi`: NVMe-MI support, default enabled.
- `python`: Python bindings, default auto.
- `json-c`, `libkmod`, `openssl`, `keyutils`, `liburing`, `libdbus`: optional dependency features.
- `tests`: build tests, default true.
- `nvme-tests`: run hardware tests, default false.
- `examples`: build examples, default true.

Documentation/install options:
- `docs`: combo of `false`, `html`, `man`, `rst`, `all`.
- `docs-build`: build documentation boolean.
- `htmldir`, `rstdir`, `dracutrulesdir`, `systemddir`, `udevrulesdir`, `nmdispatchdir`, `rundir`, and `systemctl`.

Behavioral/release options:
- `pdc-enabled`: default Persistent Discovery Controllers behavior.
- `version-tag`: override git version string.
- `pypi`: use short libnvme soname suitable for wheels.
- `check-accessors`: CI mode for accessor generator drift checks.

Plugin option:
- `plugins` is an array with a fixed list of vendor/feature plugins. If unset, all plugins are included; `[]` means no plugins.

Integration:
- Consumed throughout top-level and subdir Meson files to decide dependencies, sources, generated checks, tests, and install outputs.

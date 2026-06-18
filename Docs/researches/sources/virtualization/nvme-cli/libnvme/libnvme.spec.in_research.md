# File Research: sources/virtualization/nvme-cli/libnvme/libnvme.spec.in

This RPM spec template packages libnvme.

Package structure:
- Main package: runtime library.
- `devel` subpackage: headers, libraries, pkg-config files, and man2 pages.

Build/install:
- `%build` runs Meson with `-Ddocs=man`, `-Ddocs-build=true`, and `-Ddefault_library=both`.
- `%install` runs `meson install --destdir`.
- Template placeholders include version, license, URL, and prefix.

Integration role:
- Used by the Makefile `rpm` target after Meson config generates `libnvme.spec`.

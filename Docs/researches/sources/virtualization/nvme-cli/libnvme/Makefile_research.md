# File Research: sources/virtualization/nvme-cli/libnvme/Makefile

This is a convenience Makefile over Meson.

Targets:
- Default target builds `libnvme`.
- `update-subprojects` runs `meson subprojects update`.
- `.build` runs `meson setup`.
- `libnvme` runs `meson compile -C .build`.
- `clean` removes `.build` and purges subprojects.
- `install`, `uninstall`, `dist`, `test`, and `test-strict` wrap Meson operations.
- `rpm` creates a git archive, adds generated spec file, compresses it, and invokes `rpmbuild -ta`.

Integration role:
- Developer-friendly façade for the Meson project.
- `test-strict` runs only the libnvme suite instead of all subprojects.

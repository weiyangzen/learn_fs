# File Research: sources/virtualization/nvme-cli/nvme.control.in

- Purpose: Debian package control template for nvme-cli.
- Fields: package name `nvme`, version placeholder `@VERSION@`, amd64 architecture, dependency placeholder `@DEPENDS@`, maintainer Keith Busch, and short package description.
- Integration: Meson/package generation substitutes placeholders for the produced Debian package metadata.

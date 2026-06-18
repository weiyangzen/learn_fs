# File Research: sources/virtualization/guestfs-tools/edit/Makefile.am

## Scope

Automake rules for the C-based `virt-edit` tool.

## Build And Docs

- Builds `virt-edit` from `edit.c`.
- Includes common edit, options, Windows path helpers, utils, libguestfs, and gnulib headers.
- Links common edit/options/windows/utils libraries, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates `virt-edit.1` and website HTML from POD with general warnings.

## Tests

- Runs docs and runtime `virt-edit` tests under the repository test wrapper.

## Risks And Invariants

- Links both common edit logic and Windows path support because editing must handle guest path translation.
- This file only defines build/test wiring; tool behavior lives in `edit.c`, outside this group.

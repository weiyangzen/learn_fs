# File Research: sources/virtualization/guestfs-tools/builder/templates/Makefile.am

## Scope

Automake rules for virt-builder template fragments and kickstart/preseed generation data.

## Behavior

- Collects `*.index-fragment` files into a generated `index`.
- Distributes fragments, kickstarts, virt-install command files, preseed files, `make-template.ml`, and `validate.sh`.
- Concatenates fragments with `LANG=C` and reminds maintainers to update `index.asc` via GPG clearsigning.
- Runs `validate.sh` under the repository test wrapper.

## Risks And Invariants

- Generated unsigned `index` and signed `index.asc` must stay aligned manually.
- Concatenation order follows shell wildcard collation under `LANG=C`.

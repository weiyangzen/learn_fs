# File Research: sources/virtualization/libguestfs/daemon/rpm-c.c

Lightweight OCaml C bindings for librpm-backed package enumeration.

Important behavior:
- Without `HAVE_LIBRPM`, all entry points raise OCaml failure.
- With librpm, initializes rpm config, creates a transaction set, starts a package iterator, and returns package records to OCaml.
- Disables signature checking when `RPMVSF_MASK_NOSIGNATURES` is available.
- Extracts name, version, release, arch, URL, summary, description, and epoch.
- Converts null string fields to empty strings in the OCaml result.
- Maintains static rpm transaction and iterator until end.

Filesystem relevance: package inventory for RPM-based guests, reading the guest RPM database via librpm context.

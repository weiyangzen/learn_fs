# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/discovery.h

## Purpose

`nvme/discovery.h` defines common enums used by libnvme discovery APIs to describe NVMe log pages and features: their kind, scope, discovery evidence source, required request fields, support state, and command-set applicability.

## Main Interfaces

For log pages, it defines `nvme_log_disc_kind_t`, `nvme_log_disc_scope_t`, `nvme_log_disc_source_t`, and `nvme_log_disc_fields_t`. These classify logs as mandatory/optional/vendor-specific, scoped to controller/NVM subsystem/namespace, sourced from spec/identify/database/command probing, and requiring LSP/LSI/RAE/NSID.

For features, it defines controller/namespace scope, get-feature required fields, set-feature required fields, feature output locations, feature flags for broadcast namespace support, feature kind, command-set applicability, and implementation status.

`nvme_feat_impl_t` allows discovery to report unknown, unsupported, or supported, reflecting the fact that pre-NVMe-2.x devices often have no standard feature-support enumeration.

## Runtime Use

No logic is implemented here. Discovery code populates these enum values after combining specification rules, identify-controller bits, internal vendor databases, and command-based probing.

## Dependencies

The header is self-contained with C++ guards.

## Risks and Invariants

The flags are bitmasks; consumers may combine values. New discovery flags must not collide with existing bits.

The distinction between unknown and unsupported is important for pre-2.x devices where absence of evidence is not proof of absence.

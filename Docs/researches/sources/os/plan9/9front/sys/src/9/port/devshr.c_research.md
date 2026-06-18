# File Research: sources/os/plan9/9front/sys/src/9/port/devshr.c

Purpose: Implements `#σ` / `#σc`, a shared mount-table device for publishing named shared trees and mount points.

Key logic:
- `Shr` objects are named shared directories with an embedded `Mhead`; `Mpt` objects wrap `Mount` entries and hold owner/permission metadata.
- Attaching `#σ` exposes read/use view; attaching `#σc` exposes control view for creating/removing/renaming shared roots and mount points.
- Walking a shared root in normal view delegates remaining path walk into mounted channels in that shared mount list.
- Creating under `#σc` creates shared roots; creating under a controlled shared root creates named mount slots.
- Writing an fd to a mount slot attaches the fd through `mntattach` and installs the resulting channel as the mount target.
- Opening a mount-point file returns the posted mounted channel if mode-compatible.
- Read on normal shared roots uses `unionread` over the shared `Mhead`; read on control roots lists control entries.
- `shrrenameuser` updates owners across shared roots and mount points.

Dependencies and integration:
- Integrates directly with Plan 9 mount structures (`Mhead`, `Mount`), `createdir`, `mntattach`, `unionread`, and namespace permission checks.

Risks and notes:
- Creation and removal require `canmount`; `none` cannot create control entries.
- Mount target replacement closes the old backing channel after swapping under the mount lock.
- Permission behavior differs between normal and control views; normal shared roots mask write bits.

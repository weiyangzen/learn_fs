# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smbsrv.conf

## Purpose
Driver configuration file for the illumos SMB server pseudo device.

## Main Behavior
- Contains only the CDDL/license header, legacy ident comment, and one driver configuration directive.
- Declares `name="smbsrv" parent="pseudo";`, placing `smbsrv` under the pseudo-device parent.

## Integration Points
- Consumed by illumos driver configuration machinery when installing or attaching the SMB server kernel module.
- Complements the SMB server implementation files under `fs/smbsrv`.

## Risks and Notes
- No tunables or properties are defined here.
- Any runtime SMB server policy is configured elsewhere; this file only establishes the pseudo-device relationship.

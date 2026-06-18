<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate

## Purpose

`samba-gpupdate` applies, unapplies, or reports resultant Group Policy settings for Samba clients.

## Important APIs, Types, and Functions

It imports `apply_gp()`, `unapply_gp()`, `GPOStorage`, `rsop()`, many machine and user client-side extension classes, `get_gp_client_side_extensions()`, `Credentials`, and `logger_init()`. Options include `--unapply`, `--target`, `--force`, and `--rsop`.

## Control Flow

The script parses Samba3 options and credentials, determines the target username for Computer or User policy, switches to machine credentials for fetching GPO lists, initializes logging, opens a TDB-backed GPO cache in the cache directory, builds the extension list for the selected target, loads configured extension plugins, then calls `rsop`, `apply_gp`, or `unapply_gp`.

## State and Persistence Behavior

It reads and writes the `gpo.tdb` cache and can mutate local system state through policy extensions: access rules, Kerberos settings, scripts, sudoers, smb.conf, messages, symlinks, files, OpenSSH, MOTD/issue, GNOME, certificates, browsers, firewalld, cron, and drive maps.

## Dependencies and Integration Points

It depends heavily on Samba GP Python modules, local smb.conf, machine credentials, SYSVOL/GPO access, and extension plugin loading.

## Risks and Edge Cases

Policy extensions can alter security-sensitive local configuration. User-target identity uses initial credentials, while GPO retrieval uses machine credentials. Extension ordering matters. Failed partial application depends on extension rollback semantics.

## Test Signals

Tests should cover Computer/User targets, force reapply, unapply, RSOP-only mode, extension discovery, missing machine credentials, cache persistence, and representative extension side effects in a sandbox.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-gpupdate -->

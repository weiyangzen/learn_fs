<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in -->
# sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in

## Purpose

Manual-page template documenting `ksmbd.conf`, the share and global configuration file consumed by mountd.

## Important APIs, Types, and Functions

Documents file format, section/key syntax, comments, duplicate semantics, share names, user mapping, and global/share parameters such as interfaces, protocol limits, guest settings, signing, encryption, masks, user lists, veto files, VFS objects, and connection limits.

## Control Flow

The template is rendered by autotools or Meson by substituting sysconfdir and version. Runtime code implements the documented parser and behavior in config_parser and management modules.

## State and Persistence Behavior

Persistent state described is `@sysconfdir@/ksmbd/ksmbd.conf` and example config. `ksmbd.addshare` rewrites this file and can notify mountd by SIGHUP.

## Dependencies and Integration Points

Integrated with addshare, mountd, config_parser, management/share, and system packaging.

## Risks and Edge Cases

Documentation must remain synchronized with `KSMBD_SHARE_CONF`, defaults, parser semantics, and compile-time Kerberos support. Some options are commented out or marked not retained by addshare.

## Test Signals

Tests include generated man-page substitution, option/default parity checks against parser tables, and manual examples parsed by config_parser.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in -->

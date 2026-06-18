<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in -->
# sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in

## Purpose

Manual-page template for the ksmbd password database format.

## Important APIs, Types, and Functions

Documents `name:password` lines, user-name UTF-8/length/colon constraints, and NT password hash derivation: UTF-8 password to UTF-16LE, MD4, then Base64 with padding.

## Control Flow

Rendered by build systems and referenced by adduser and mountd docs. Runtime parsing is performed by config_parser/user management.

## State and Persistence Behavior

Persistent state is `@sysconfdir@/ksmbd/ksmbdpwd.db`, modified by `ksmbd.adduser` and reloaded by mountd.

## Dependencies and Integration Points

Depends on adduser, md4_hash, tools charset/Base64 helpers, and user management.

## Risks and Edge Cases

Docs must match actual max password length and hash encoding behavior. Command-line password use has operational secrecy concerns not fully captured by file format docs.

## Test Signals

Tests include generated substitution, known hash examples, invalid user lines, empty passwords, and reload after database updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in -->

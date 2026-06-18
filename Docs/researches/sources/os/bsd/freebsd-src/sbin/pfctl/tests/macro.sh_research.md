# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/macro.sh

## Purpose
Shell ATF test for pfctl macro definitions containing spaces.

## Main Elements
- Defines ATF test case `space`.
- Writes invalid macro assignment with quoted name containing a space and expects `pfctl -nvf` to fail.
- Writes valid macro assignment with unquoted name and quoted value containing spaces and expects success.
- Cleans up temporary `pf.conf`.

## Dependencies And Integration
Requires `pf` kernel module and uses `atf_check`.

## Risk Notes
Protects macro-name grammar and quoted-value handling.

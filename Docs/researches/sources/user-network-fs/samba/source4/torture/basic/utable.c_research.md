# sources/user-network-fs/samba/source4/torture/basic/utable.c

## Purpose
This file probes Unicode filename acceptance and case-equivalence behavior. It can generate a `valid.dat` table of accepted Unicode codepoints and exercise server case folding through file aliases.

## Important APIs, types, and functions
Exported functions are `torture_utable()` and `torture_casetable()`. Helper `form_name()` converts a codepoint to a `\utable\...` filename. It uses `convert_string(CH_UTF16, CH_UNIX, ...)`, `SSVAL`, `smbcli_open()`, `smbcli_nt_create_full()`, `smbcli_qpathinfo_alt_name()`, `smbcli_qfileinfo()`, `smbcli_read()`, `smbcli_write()`, wildcard unlink/rmdir, and `sys_write_v()`.

## Control flow
`torture_utable()` loops over codepoints `1..0xffff`, converts each to a filename with a long extension, tries to create it, asks for the alternate name, and records codepoints whose alternate name is not the generic `X_A_L...` pattern. It writes the 65536-byte validity bitmap to local `valid.dat`. `torture_casetable()` loops codepoints, creates/opens corresponding filenames, reads existing equivalence data if another codepoint maps to the same name, writes the current codepoint, and reports equivalence sets.

## State and persistence
Server state is under `\utable` and is cleaned by unlink/rmdir. Local durable output is `valid.dat` in the current working directory. Large in-memory arrays include `valid[0x10000]` and `equiv[0x10000][8]`.

## Dependencies and integration points
The test depends on Samba charset conversion, server Unicode filename handling, short-name generation, and case-insensitive filesystem behavior. It is sensitive to locale/charset configuration.

## Risks
The full Unicode loop is expensive and may produce many server operations. `valid.dat` is written outside the research tree/test share and can surprise callers. Case table probing can be noisy and depends heavily on filesystem normalization semantics.

## Test signals
Signals are counts of allowed characters and alternate-name-allowed characters, printed equivalence groups, conversion failures, failed creates for specific codepoints, and successful creation of `valid.dat`.

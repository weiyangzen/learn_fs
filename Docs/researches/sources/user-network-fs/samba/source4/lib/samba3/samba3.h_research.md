# sources/user-network-fs/samba/source4/lib/samba3/samba3.h

## Purpose

`samba3.h` is the small public header for Samba3 compatibility helpers in this directory. It exposes smbpasswd hash conversion routines.

## Important APIs, Types, and Functions

The header declares `smbpasswd_gethexpwd()` to parse a 32-character hex password hash into `struct samr_Password`, and `smbpasswd_sethexpwd()` to format a `struct samr_Password` or placeholder into smbpasswd text.

## Control Flow

There is no runtime control flow. Including translation units get security and SAMR generated types and the two helper prototypes.

## State and Persistence Behavior

The header defines no state. The declared functions allocate talloc-owned return values and are intended for parsing or emitting smbpasswd file fields.

## Dependencies and Integration Points

It includes generated `security.h` and `samr.h` types. `smbpasswd.c` implements the prototypes, and `wscript_build` compiles them into the private `smbpasswdparser` library.

## Risks and Edge Cases

The API exposes only hash-field conversion, not full smbpasswd line parsing. Callers must handle NULL returns for invalid input and own talloc lifetimes correctly.

## Test Signals

Compile coverage with `smbpasswd.c` catches prototype drift. Unit tests should parse valid/invalid 32-hex strings and format real, NULL, and password-not-required values.

Source-read signal: reviewed complete local file (29 lines).

# sources/user-network-fs/samba/source4/torture/drs/python/cracknames.py Research

## Purpose
This Python test module validates DRSUAPI `DsCrackNames` behavior for common Active Directory name formats, including round trips through GUID form and edge cases for multi-valued or missing service principal names.

## Important APIs, Types, And Functions
`DrsCracknamesTestCase` extends `drs_base.DrsBaseTestCase`. `setUp()` binds to DC1 through `_ds_bind()`, creates an OU and a user with `sAMAccountName`, `userPrincipalName`, `servicePrincipalName`, and `displayName`, deletes and re-adds the user, and defines the supported `DS_NAME_FORMAT` constants. `_do_cracknames()` builds `drsuapi.DsNameRequest1`, sets codepage, language, offered and desired formats, and calls `self.drs.DsCrackNames()`.

## Control Flow
`test_Cracknames()` cracks the user's FQDN DN to GUID, then loops over every configured name format, converting GUID to that format and back to GUID while asserting `DRSUAPI_DS_NAME_STATUS_OK`. `test_MultiValuedAttribute()` creates a user with two SPNs and expects `DRSUAPI_DS_NAME_STATUS_NOT_UNIQUE` for GUID-to-SPN. `test_NoSPNAttribute()` creates a user without SPN and expects `DRSUAPI_DS_NAME_STATUS_NOT_FOUND` for GUID-to-SPN.

## State And Persistence
The test creates an OU and user objects in DC1. `tearDown()` deletes the main user and OU; individual tests delete their extra users. Failure before cleanup can leave directory objects. The delete and re-add in setup exercises re-created object behavior and reduces stale-state assumptions.

## Dependencies And Integration Points
The module depends on `drs_base`, `samba.tests`, LDB, and `samba.dcerpc.drsuapi`. It requires the base two-DC environment even though its operations primarily bind and mutate DC1.

## Risks And Test Signals
Signals are `ctr.count == 1` and exact `ctr.array[0].status` values. Risks include fixed object names colliding with leftovers, partial cleanup on failure, and assumptions about supported DS name formats compared with Windows.

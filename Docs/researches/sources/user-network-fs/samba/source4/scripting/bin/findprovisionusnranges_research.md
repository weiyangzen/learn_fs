<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges -->
# sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges

## Purpose

`findprovisionusnranges` identifies update sequence number ranges likely created by provision or upgradeprovision activity.

## Important APIs, Types, and Functions

It uses Samba option parsing, credentials with Kerberos disabled, `get_paths()`, `findprovisionrange()`, `print_provision_ranges()`, LDB rootDSE searches, `ndr_unpack()`, and `misc.GUID` for invocation ID decoding.

## Control Flow

The script loads configuration and credentials, opens `sam.ldb`, derives the base DN from the realm, reads `dsServiceName`, follows it to the NTDS settings object, extracts `invocationId`, computes provision-range buckets, and prints ranges affecting more than a fixed minimum object count.

## State and Persistence Behavior

It reads databases and optionally writes result files through `print_provision_ranges()` when `--storedir` is provided. It does not modify AD data.

## Dependencies and Integration Points

It depends on Samba upgrade helper APIs, local provision paths, LDB controls, and DSDB metadata.

## Risks and Edge Cases

It assumes local database layout and realm-derived base DN. Missing `dsServiceName` or invocation ID exits. The minimum threshold is hard-coded to five objects.

## Test Signals

Tests should run against known provisioned databases, databases without invocation ID, `--storedir` output, and upgraded databases with recognizable high-volume USN ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/findprovisionusnranges -->

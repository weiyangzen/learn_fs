<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/renamedc -->
# sources/user-network-fs/samba/source4/scripting/bin/renamedc

## Purpose

`renamedc` renames a Samba domain controller account and related local secrets/configuration records.

## Important APIs, Types, and Functions

It uses Samba option parsing, `get_paths()`, `get_ldbs()`, `find_provision_key_parameters()`, `secretsdb_self_join()`, `generate_random_machine_password()`, and LDB transaction APIs.

## Control Flow

The script requires `--oldname` and `--newname`, opens SAM and secrets databases, starts transactions, finds the old DC computer object by `serverReferenceBL`, ensures the new computer name is unused, gathers provision parameters, renames the computer DN, replaces password, `sAMAccountName`, and `dNSHostName`, performs a secrets self-join with the new machine password and current KVNO, updates RID set reference, renames the server object in Sites configuration, prepares and commits both transactions, then rewrites `netbios name` in smb.conf.

## State and Persistence Behavior

It mutates `sam.ldb`, `secrets.ldb`, and smb.conf. Database changes are transactional across separate LDBs using prepare/commit, but smb.conf rewrite happens after database commits.

## Dependencies and Integration Points

It depends on Samba provision/upgrade helpers, local DB paths, secrets database semantics, RID set references, and site configuration objects.

## Risks and Edge Cases

Renaming a DC is high risk. smb.conf update is not transactional with database commits. Search filters interpolate names directly. The script assumes exactly one old DC result and one RID set. It leaves broader DNS/SPN/replication side effects to other tooling or later checks.

## Test Signals

Tests should use disposable DC databases, validate missing/duplicate names, transaction rollback on injected failure, secrets update, RID set and server object rename, smb.conf rewrite, and post-rename `dbcheck`/replication behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/renamedc -->

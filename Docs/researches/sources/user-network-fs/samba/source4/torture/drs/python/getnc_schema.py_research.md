# sources/user-network-fs/samba/source4/torture/drs/python/getnc_schema.py Research

## Purpose
This module tests schema partition replication scenarios, especially schema objects with dependency links that cross replication chunks and linked attributes on schema objects. It is explicitly gated because repeated execution can damage Windows Active Directory test environments.

## Important APIs, Types, And Functions
The module asserts `PLEASE_BREAK_MY_WINDOWS=1` before tests can run. `SchemaReplicationTests.setUp()` captures credentials, sets command-line auth, chooses DC1 as source and DC2 as destination, disables replication on DC1, and initializes uniqueness state. `do_repl()` temporarily enables replication, runs `samba-tool drs replicate`, retries once after 10 seconds on failure, disables replication again, and asserts success. `get_unique()`, `unique_gov_id_prefix()`, and `unique_cn_prefix()` generate schema-safe unique names and OIDs.

## Control Flow
`test_poss_superiors_across_chunk()` creates 150 `classSchema` objects chained through `systemPossSuperiors`, handles schema update races, modifies them in reverse order, replicates the schema partition, and verifies destination objects. `test_create_linked_attribute_in_schema()` creates an auxiliary class that may contain `managedBy`, creates a schema object pointing to a user, and verifies forward and backlink attributes. `test_schema_linked_attributes()` repeats the linked schema-object pattern across multiple objects and validates destination links after replication.

## State And Persistence
This file permanently creates schema classes and schema objects. It also creates users and toggles replication options. The top-level environment assertion is a deliberate safety gate because schema changes accumulate and can break Windows AD after several runs. Teardown re-enables replication but does not delete schema objects.

## Dependencies And Integration Points
The module depends on `drs_base`, LDB LDIF APIs, SambaTool DRS replication, environment variables `DC1`, `DC2`, `SMB_CONF_PATH`, credentials, and writable schema permissions. It exercises schema update behavior and DRS chunking in a live directory.

## Risks And Test Signals
Signals are successful destination schema object searches, correct `managedBy` forward links, and exact `managedObjects` backlink sets. Risks are severe by design: permanent schema mutation, replication option side effects, possible Windows AD breakage, timing retries, and no cleanup for schema objects.

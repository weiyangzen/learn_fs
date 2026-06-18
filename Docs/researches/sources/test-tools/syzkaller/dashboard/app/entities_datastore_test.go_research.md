# sources/test-tools/syzkaller/dashboard/app/entities_datastore_test.go

Purpose: focused regression coverage for loading legacy bug subsystem tags into the modern labels representation.

Important APIs/types/functions: `TestOldBugTagsConversion`, `Bug.Load`, `BugTags202304`, `BugTag202304`, `BugLabel`, `SubsystemLabel`, and `db.SaveStruct`.

Control flow: the test serializes an old-shaped bug containing `Tags.Subsystems`, loads those datastore properties into a modern `Bug`, and asserts the resulting `Labels` contain subsystem labels with preserved `Value` and `SetBy`.

State/persistence: no live datastore is used; it exercises datastore property serialization in memory.

Dependencies/integration: depends on App Engine datastore property APIs and `testify/require`; protects compatibility for old production entities.

Risks/test signals: covers only tag conversion, not `HeadReproLevel` or crash reference migrations. Signal is exact struct equality for the converted bug.

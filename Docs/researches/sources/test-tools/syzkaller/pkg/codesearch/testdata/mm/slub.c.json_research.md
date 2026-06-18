# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c.json

Purpose: Empty golden database for `mm/slub.c`, which has no extractable definitions.

Important APIs/types/functions: No definitions.

Control flow: Static JSON data only.

State and persistence behavior: Persists the expected empty clangtool result as `{}`.

Dependencies/integration points: Compared by clangtool golden tests and merged by `tooltest.LoadOutput`.

Risks: Empty JSON still needs to deserialize into a valid `Database`. If the tool starts emitting comments/macros for this fixture, this golden will change.

Test signals: Confirms the extractor can produce and consumers can accept empty database output.

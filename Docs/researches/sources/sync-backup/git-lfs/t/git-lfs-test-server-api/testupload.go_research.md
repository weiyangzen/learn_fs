# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testupload.go

## Purpose
Upload-side compliance tests for the Git LFS batch API probe. It verifies whether the server asks clients to upload missing objects, skips objects already present, and rejects invalid upload requests with proper object-level errors.

## Important APIs, Functions, and Control Flow
`uploadAllMissing` requires each missing OID to return an `upload` relation. `uploadAllExists` requires existing OIDs not to include upload links. `uploadMixed` uses OID sets and deterministic interleaving to validate mixed responses. `uploadEdgeCases` submits malformed SHA lengths, invalid SHA characters, negative sizes, and a valid zero-size object; invalid cases must return code 422 with no upload relation, while zero size must receive an upload link.

## State, Persistence, and Dependencies
State comes from `main.go` test object slices. The file depends on shared batch helpers, `tools.StringSet`, `bytes.Buffer`, and `tq.Transfer.Rel`. It accumulates all validation problems into a single returned error string per test.

## Integration Points, Risks, and Test Signals
The `init` function registers four upload tests. The tests assert batch API metadata rather than performing actual object upload for the returned links. Risks include strict expectation of 422 for validation failures and lack of error message matching beyond locally stored reasons used in failure text. Primary signals are response count, presence or absence of upload relations, and error code correctness for invalid OIDs and sizes.

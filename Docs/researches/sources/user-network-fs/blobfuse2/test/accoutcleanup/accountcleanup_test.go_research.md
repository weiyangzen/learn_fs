<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go -->
# sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go

## Purpose
Nightly cleanup test that deletes temporary Azure Blob containers left behind by pipeline/test runs.

## Important APIs, Types, and Functions
`getGenericCredential` reads `STORAGE_ACCOUNT_NAME` and `STORAGE_ACCOUNT_KEY` and creates a shared-key credential. `getGenericServiceClient` builds a Blob service client. `TestDeleteAllTempContainers` lists containers and deletes names beginning with `fuseutc` or having length 40. `TestMain` simply runs tests.

## Control Flow and State
The test authenticates to a real storage account, pages through all containers, and issues delete calls for matching names. It logs delete failures but continues.

## Dependencies and Integration Points
Uses Azure Storage Go SDK `azblob/service`, real storage account credentials, and network access. Excluded under `unittest` build tag.

## Risks and Edge Cases
This is destructive. The length-40 heuristic can delete non-test containers if naming collides. Missing credentials call `log.Fatal`, aborting the test process. It does not check creation time or metadata ownership.

## Test Signals
Successful completion indicates cleanup attempts ran. Logs show deleted containers and failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go -->

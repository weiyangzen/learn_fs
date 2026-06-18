# sources/user-network-fs/blobfuse2/component/azstorage/azauth_test.go

Purpose: provides integration tests for azstorage authentication modes. The tests verify that invalid auth/account configurations fail and that valid key, SAS, MSI, SPN-related, and Azure CLI configurations can set up and test a storage pipeline.

Important APIs/types/functions: `storageTestConfiguration` maps `~/azuretest.json` fields for block and ADLS accounts, containers, keys, SAS tokens, MSI identifiers, SPN credentials, skip flags, and proxy address. `authTestSuite.SetupTest` configures a base logger and loads the JSON file. `validateStorageTest` builds `NewAzStorageConnection`, runs `SetupPipeline`, and calls `TestPipeline`. `generateEndpoint` builds Blob or DFS endpoints.

Control flow: each test constructs `AzStorageConfig` with an embedded `azAuthConfig`, then validates either expected failure or successful pipeline authentication. Invalid cases include unsupported auth mode, invalid account type, empty or malformed shared key, and empty SAS. Positive cases cover block/adls shared key, SAS, container SAS, MSI by application/resource/object ID, and Azure CLI. SAS tests also exercise `UpdateServiceClient("saskey", ...)`.

State and persistence behavior: tests read external persistent config from the user's home directory and write logs to `./logfile.txt`. They do not create repository state. Runtime storage clients authenticate against real Azure services.

Dependencies/integration: depends on local `common` and `log`, the azstorage configuration/connection stack, testify suite/assert, the OS home directory, and a live Azure account configuration. The build tag `!authtest` means these tests are included unless the `authtest` tag is set, but they still require external setup.

Risks: tests call `os.Exit(1)` from setup on missing config or logger setup failures, which can abort the whole package test run rather than reporting a normal test failure. They are environment-dependent and may be flaky due to network, Azure service state, credential expiry, or local Azure CLI login. Secrets are loaded from a home-dir JSON file, so developer machines and CI need careful secret handling.

Test signals: useful as broad live-auth smoke tests across account types and auth modes. They do not mock credential construction, do not cover workload identity explicitly, and do not isolate individual auth wrapper failure branches beyond the storage pipeline boundary.

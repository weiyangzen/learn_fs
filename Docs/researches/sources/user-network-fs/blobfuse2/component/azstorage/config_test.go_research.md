# sources/user-network-fs/blobfuse2/component/azstorage/config_test.go

## Purpose
Unit-style `testify/suite` coverage for `config.go` parsing and dynamic reconfiguration. The tests focus on validation failures, default values, legacy flags, auth selection, proxy normalization, reloadable SAS configuration, compression toggles, max list result sizing, and rate-limit defaults without requiring Azure service access.

## Important APIs, Types, and Functions
`configTestSuite` provides `SetupTest()` that installs a silent debug logger. Each test constructs an `AzStorage` and `AzStorageOptions`, optionally mutates the global config package with `config.Set*`, calls `ParseAndValidateConfig()` or `ParseAndReadDynamicConfig()`, and asserts fields on `az.stConfig`. `TestConfigTestSuite()` registers the suite.

The covered test methods are `TestEmptyAccountName`, `TestEmptyAccountType`, `TestInvalidAccountType`, `TestUseADLSFlag`, `TestBlockSize`, `TestProtoType`, `TestProxyConfig`, `TestMaxResultsForList`, `TestAuthModeNotSet`, `TestAuthModeKey`, `TestAuthModeSAS`, `TestAuthModeMSI`, `TestAuthModeSPN`, `TestOtherFlags`, `TestCompressionType`, `TestSASRefresh`, and `TestRateLimitConfig`.

## Control Flow, State, and Persistence
Most tests defer `config.ResetConfig()` to isolate global config keys. Account-type tests verify empty account names fail, invalid type strings fail, and the legacy `azstorage.use-adls` setting overrides an otherwise invalid type string into ADLS or block. Block-size coverage verifies MB-to-byte conversion and rejection over `blockblob.MaxStageBlockBytes`, though the oversized case passes a byte-valued SDK constant into an MB-valued option. Protocol and proxy tests exercise `use-https`, `UseHTTPS`, `UseHTTP`, HTTP proxy rejection under HTTPS, HTTPS proxy acceptance, and protocol/trailing slash formatting.

Auth tests verify default MSI selection, key mode requiring `AccountKey`, SAS mode requiring `SaSKey`, MSI optional identity fields and mutual exclusion, and SPN requiring client ID, tenant ID, and one credential source. Dynamic config tests confirm `disable-compression` only takes effect when explicitly set, SAS reload calls through a synthetic `BlockBlob` auth object, and read/IOPS caps default to `-1` then accept positive values. State is limited to the in-memory `AzStorage` struct and the shared config registry.

## Dependencies and Integration Points
Depends on `testing`, Azure SDK block-blob constants, Blobfuse `common`, `config`, and `log` packages, and `testify/assert`/`suite`. It reaches into package-private `AzStorage` and `AzStorageConfig` fields because it is in package `azstorage`, making it a close regression suite for the config parser rather than a public API test.

## Risks and Test Signals
The suite gives fast signal for parser invariants and default propagation, but it does not start real pipelines or validate actual credentials. Risks include reliance on global config cleanup, missing coverage for AZCLI, workload identity, CPK failure paths, blob filter read-only enforcement, Active Directory endpoint formatting, auth resource, telemetry, ACL preservation, and mount-all-containers behavior. Several tests intentionally expect later validation errors while still checking partial state, which is useful for parser ordering but could mask changes where earlier failures prevent state population.

# sources/sync-backup/syncthing/lib/config/config_test.go

## sources/sync-backup/syncthing/lib/config/config_test.go

Purpose: Broad integration and compatibility test suite for the `config` package.

Important APIs/types/functions: Defines stable test device IDs, a fake filesystem populated from `testdata`, helpers `copyAndLoad`, `loadTest`, `loadWrapTest`, `wrap`, `startWrapper`, and `defaultConfigAsMap`. Tests cover `New`, XML/JSON load paths, wrapper save/load, folder filesystem behavior, GUI URL/password/session behavior, migrations, duplicates, ignored remote state, ID validation, folder defaults, xattr filters, untrusted devices, and tag copying.

Control flow and state: The suite copies fixtures into a fake filesystem before load so migrations and save paths can mutate temporary data. Wrapper tests start `Serve` in a goroutine and stop it via context cancellation. Many tests compare fully prepared configs against expected structs, which validates both default filling and migration side effects.

Dependencies and integration: Uses `messagediff`, `bcrypt`, fake filesystems, `events.NoopLogger`, `protocol`, `build` platform flags, and the real wrapper service. It is the primary regression guard for `config.go`, `migrations.go`, enum marshalers, `folderconfiguration.go`, and XML fixtures.

Risks and test signals: Strong signals include `TestDeviceConfig` loading historical versions to `CurrentVersion`, duplicate-folder failure, empty-path failure, ignored-folder pruning, `ReadJSON` invalid ID rejection, `TestUntrustedIntroducer`, and `TestCopy` deep-copy behavior. Some behavior is platform-specific (`TestIssue1262`, Windows line endings), and `TestSharesRemovedOnDeviceRemoval` is skipped due to a known hang.

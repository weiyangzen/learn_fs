# sources/user-network-fs/rclone/fs/config/config_test.go

Purpose: externally tests config loading through the installed `configfile` storage implementation.

Important APIs/functions: package init calls `configfile.Install`. `TestConfigLoad` switches `configPath` to `./testdata/plain.conf`, clears any config password, then inspects sections and keys from `config.Data()`.

Control flow: saves old config path, sets a test path, defers restoration, and asserts loaded section/key order matches expectations.

State and persistence behavior: mutates global `configPath` and password state during the test and restores config path afterward. It relies on `config.Data()` storage loading the selected file.

Dependencies and integration points: imports config as an external package, plus `configfile`, to verify the public install/load path rather than internals.

Risks: limited scope; it does not test save, missing config, environment overrides, or encrypted load. Global config path mutation makes restoration important.

Test signals: basic integration signal that configfile storage can load the bundled plaintext fixture.

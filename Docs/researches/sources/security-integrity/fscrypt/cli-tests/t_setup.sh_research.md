# sources/security-integrity/fscrypt/cli-tests/t_setup.sh

## Purpose
Tests global and filesystem setup command behavior.

## Control Flow and Integration
Verifies global setup creates `fscrypt.conf`, global setup also creates root `.fscrypt`, rejects existing config on cancel or quiet mode, accepts replacement interactively and with `--force`, sets up a filesystem, rejects already setup filesystem, rejects filesystem setup without config, and rejects bad config file.

## State and Risks
Mutates global test config and `.fscrypt` metadata directories. Covers `createGlobalConfig`, `setupFilesystem`, confirmation handling, config parsing errors, and already-setup errors.

## Test Signals
Good coverage for setup idempotence, force/quiet semantics, and config prerequisite handling.

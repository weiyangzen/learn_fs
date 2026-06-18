# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-aud.cfg

## Purpose

This test SciTokens config requires a single accepted audience for the localhost issuer.

## Important APIs, Types, And Functions

- `[Global] audience = testing.com`
- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test installs this config, restarts xrootd, then expects tokens with `aud=testing.com` to succeed and tokens without an audience to fail.

## State And Persistence

It is copied to `/etc/xrootd/scitokens.cfg` during tests and parsed into plugin runtime state.

## Dependencies And Integration Points

Consumed by `XrdAccSciTokens::Reconfig()` and SciTokens enforcer audience checking.

## Risks And Edge Cases

- Issuer URL must match the token issuer exactly, including scheme and host.
- The base path `/` grants scope-derived paths across the exported namespace for matching token scopes.

## Test Signals

Expected signal is pass for a valid localhost token with `aud=testing.com`, fail for no-audience and wrong-audience variants.

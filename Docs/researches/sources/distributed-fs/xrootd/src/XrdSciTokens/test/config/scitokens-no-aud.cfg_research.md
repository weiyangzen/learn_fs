# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-no-aud.cfg

## Purpose

This test config defines a localhost issuer without configuring a global audience.

## Important APIs, Types, And Functions

- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test expects a token without `aud` to succeed and a token carrying `aud=testing.com` to fail when this config is installed.

## State And Persistence

It is copied to `/etc/xrootd/scitokens.cfg` during tests.

## Dependencies And Integration Points

It exercises `XrdAccSciTokens::Reconfig()` behavior when `m_audiences_array` contains only the null terminator.

## Risks And Edge Cases

- Audience-less acceptance depends on SciTokens library behavior with an empty audience list.
- This config is intentionally minimal and broadly maps scopes under `/`.

## Test Signals

Expected signal is successful read with no `aud` claim and failure when an audience claim is present.

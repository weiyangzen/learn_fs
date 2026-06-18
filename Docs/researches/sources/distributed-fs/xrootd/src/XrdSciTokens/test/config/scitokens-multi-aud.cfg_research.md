# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-multi-aud.cfg

## Purpose

This test config accepts two audience values for the localhost issuer.

## Important APIs, Types, And Functions

- `[Global] audience = testing.com, https://another.com`
- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test copies this config, restarts xrootd, then verifies either configured audience succeeds while no audience and wrong audience fail.

## State And Persistence

It is static test config parsed into runtime audience vector state.

## Dependencies And Integration Points

It exercises comma/space splitting in `XrdAccSciTokens::Reconfig()` and SciTokens enforcer audience validation.

## Risks And Edge Cases

- Audience parsing splits on comma and space, so values containing spaces require `audience_json` instead.
- The URL audience includes `https://`; exact token claim matching is required.

## Test Signals

Expected test signals are successful reads for `testing.com` and `https://another.com`, and failures for absent or `wrong.com` audiences.

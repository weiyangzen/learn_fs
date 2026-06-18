# sources/distributed-fs/xrootd/src/XrdSciTokens/configs/scitokens.cfg

## Purpose

This is a sample SciTokens plugin configuration showing global audience syntax and two issuer sections.

## Important APIs, Types, And Functions

- Commented `[Global]` examples show `audience` and `audience_json`.
- `[Issuer OSG-Connect]` sets issuer `https://scitokens.org/osg-connect`, `base_path=/stash`, and `map_subject=True`.
- `[Issuer CMS]` sets issuer `https://scitokens.org/cms`, `base_path=/user/cms`, and `map_subject=False`.

## Control Flow

When used as the plugin config, `Reconfig()` parses issuer sections and maps token scopes under each base path. The OSG issuer maps token subject to local username; CMS does not.

## State And Persistence

It is static configuration text. Runtime state is created by `XrdSciTokensAccess.cc` when parsed.

## Dependencies And Integration Points

It follows the INI syntax consumed by `OverrideINIReader` and the keys recognized by `XrdAccSciTokens::Reconfig()`.

## Risks And Edge Cases

- The global audience examples are commented, so tokens with an `aud` claim may be rejected depending on SciTokens library semantics when no audience is configured.
- `map_subject=True` assumes subjects are safe local usernames; newer code validates explicit username claims, but subject/default mapping policy still needs operator care.

## Test Signals

Config tests should parse this file and verify both issuers appear, base paths canonicalize, and sample tokens for each issuer map according to `map_subject`.

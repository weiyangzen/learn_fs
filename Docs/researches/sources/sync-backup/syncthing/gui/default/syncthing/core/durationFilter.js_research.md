# sources/sync-backup/syncthing/gui/default/syncthing/core/durationFilter.js

## Purpose
This AngularJS filter converts a duration in seconds into a compact localized string such as days/hours/minutes/seconds, with caller-controlled precision.

## Important APIs, types, and functions
It registers `duration` on `syncthing.core` and injects `$translate`. The filter signature is `duration(input, precision)`, where `precision` defaults to `"s"` and must be one of `"d"`, `"h"`, `"m"`, or `"s"`. It uses `humanizeDuration(input * 1000, { language, maxDecimalPoints: 0, units, fallbacks })` when a current translation language is available. A local `SECONDS_IN` map powers a manual English-style fallback.

## Control flow
The filter parses `input` as base-10 integer seconds and determines the current language from `$translate.use()`, replacing hyphens with underscores for humanize-duration language codes. For Chinese languages it adds `zh_TW` as a fallback, then adds the base language when the locale is regional, and finally English. It builds the allowed units by popping lower-precision units according to the requested precision. If humanize-duration succeeds, the localized string is returned. If language resolution is absent or humanize-duration throws, it falls back to manual `d h m s` formatting and returns `<1<precision>` for sub-unit values.

## State and persistence behavior
The filter itself is stateless. It reads current translation state from `$translate`, and logs caught humanize-duration errors to `console`.

## Dependencies and integration points
Dependencies are AngularJS, `$translate`, the global `humanizeDuration` library, and the translation locale selected by `LocaleService`. It integrates with locale catalogs indirectly because `$translate.use()` controls its language choice, and with Chinese catalogs through the `zh_TW` fallback rule.

## Risks
Invalid precision returns an error string in the UI. `parseInt` can truncate fractional seconds and turn invalid strings into `NaN`, which can flow to fallback behavior oddly. The manual fallback is not localized and uses compact unit letters only. The `switch` uses fallthrough intentionally, so missing break changes would break precision filtering. If humanize-duration lacks a language and throws, users get English-like output after a console log.

## Test signals
Unit tests should cover all precision values, invalid precision, sub-unit output, zero, fractional or string inputs, Chinese language fallback (`zh-HK` to `zh_TW`), region fallback such as `en_GB` to `en`, and simulated humanize-duration exceptions.

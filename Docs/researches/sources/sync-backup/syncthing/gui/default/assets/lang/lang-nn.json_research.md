# sources/sync-backup/syncthing/gui/default/assets/lang/lang-nn.json

## Purpose

`lang-nn.json` supplies Norwegian Nynorsk translations for the Syncthing default web GUI. Like the surrounding files, it is generated from Weblate and is not intended for direct hand editing.

The file is a JSON object with 257 top-level entries, all strings. It is much more partial than the English baseline of 558 keys: 301 English keys are absent, no extra keys are present, and there are no empty string values. It also lacks the nested `theme` object found in more complete locales.

## Important APIs, Types, and Data Shape

There are no executable APIs, only static translation data. Every entry maps an English GUI phrase to a Nynorsk string. The entries cover common labels and workflows such as device/folder add dialogs, sharing, file versioning, discovery, error copy, and basic status text, but many newer or less common screens fall back to English.

Unlike the other files in this group, `lang-nn.json` does not define `theme.name.*`. Calls to `$translate.instant("theme.name." + theme)` will not find locale-specific Nynorsk theme labels; the controller's `themeName()` fallback then title-cases the raw theme ID.

Interpolation entries use the same project pattern as other locales: source keys use `{%...%}` markers while translated values use Angular `{{...}}` variables.

## Control Flow and Runtime Use

The generic loader in `syncthing/app.js` can request this file as `assets/lang/lang-nn.json` if `$translate.use('nn')` is called. Once loaded, angular-translate uses it for directives and filters whose English source phrase is present.

However, `assets/lang/valid-langs.js` does not include `nn`. That means `LocaleServiceProvider.setAvailableLocales(validLangs)` does not advertise Nynorsk to automatic browser-language matching or to the language selector. A direct `?lang=nn` query can still call `LocaleService.useLocale('nn', true)` because `useLocale` does not itself check `_availableLocales`, but Nynorsk is effectively hidden from normal UI selection and auto-detection in this snapshot.

Missing Nynorsk keys fall back to English through `$translateProvider.fallbackLanguage('en')`. This is particularly visible because more than half of the English catalog is absent.

## State and Persistence Behavior

The file is immutable static data at runtime. If a user forces Nynorsk through `?lang=nn`, `LocaleService` can persist `SYN_LANG=nn` in `localStorage` and set `<html lang="nn">` after angular-translate loads the file successfully.

Since `nn` is not in `validLangs`, a persisted `SYN_LANG=nn` can still be used on later visits, but the language selector builds its menu from `validLangs` and will not include a normal Nynorsk option.

## Dependencies and Integration Points

The runtime dependencies are the same angular-translate static loader and Angular interpolation stack used by all GUI translations. Integration with `LocaleService` is weaker than for the other files because the locale is not present in `valid-langs.js`.

The file integrates with any template or controller translation ID matching one of its 257 keys. It does not integrate with the theme display path because `theme.name.*` is absent.

## Risks

The largest risk is product exposure ambiguity: the file exists and can be loaded by locale code, but the whitelist omits `nn`. This may mean the translation is intentionally incomplete and not offered, or it may be an asset/list drift bug.

The second risk is extensive English fallback. Missing coverage includes authentication, advanced settings, block indexing, crash reporting, discovery/listener details, restore flows, local changes, login/logout strings, extended attributes, ownership, and many warning texts. A Nynorsk session will therefore present a mixed-language GUI.

Only one entry is identical to the key (`LDAP`), which is likely a technical acronym rather than a translation defect. The absence of `theme.name.*` causes theme labels to fall back to title-cased IDs.

Manual edits are likely to be overwritten because translations are generated through Weblate.

## Test Signals

Static checks should verify valid JSON, no empty values, and expected all-string top-level values for this partial file. Catalog checks should explicitly report its 301 missing keys and the absence of `theme.name.*`.

Integration checks should decide whether `nn` should be in `valid-langs.js`. If it should be user-selectable, tests should assert that the language dropdown includes it and that browser `nn` accept-language values can select it. If it is intentionally hidden, tests should still verify that a direct `?lang=nn` load either works cleanly with fallback or is deliberately blocked.

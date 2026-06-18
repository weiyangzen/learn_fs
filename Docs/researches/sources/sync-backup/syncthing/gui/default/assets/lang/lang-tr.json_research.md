# sources/sync-backup/syncthing/gui/default/assets/lang/lang-tr.json

## Purpose
`lang-tr.json` is the Turkish translation catalog for the Syncthing default web GUI. It covers the full English base catalog, including legacy GUI strings and newer features such as connection management, ownership, extended attributes, block indexing, sharing helpers, and authentication copy.

## APIs, types, and data shape
The file is a flat JSON object with 558 keys, exactly matching the 558-key English base. It exports no functions or classes. There are no missing keys, no extra keys, no empty values, and no placeholder-token mismatches. Five values remain identical to English, all acronym/protocol-style strings: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`.

## Control flow
When the selected locale is Turkish, `LocaleService.useLocale('tr', ...)` calls `$translate.use('tr')`. Angular Translate then uses this JSON table for `translate` directives, translate filters, and `$translate.instant(...)` controller calls. Dynamic values such as device names, folder labels, versions, URLs, and paths are injected through preserved interpolation placeholders.

## State and persistence behavior
The catalog itself is read-only static data. It does not update Syncthing config or local runtime state. User language selection is persisted in `localStorage` by `LocaleService` under `SYN_LANG`, and the page `lang` attribute is updated outside this file.

## Dependencies and integration points
The file depends on Angular Translate, the English source key set, `valid-langs.js` including `tr`, and the Weblate-generated asset workflow. It is integrated into the language menu through Syncthing's locale service and display-name infrastructure.

## Risks
Structural risk is low because coverage is complete and placeholders match. The remaining risks are translation quality, text length in constrained controls, and future drift if English keys are added without regenerating the Turkish catalog. Generated-file status means local patches are likely overwritten by the translation import pipeline.

## Test signals
Run JSON parse, exact key-set equality against `lang-en.json`, placeholder parity checks, and Turkish GUI smoke tests across settings, device/folder editing, encrypted folder warnings, share-by-email/SMS flows, logs, and restore/version dialogs.

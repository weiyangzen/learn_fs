# sources/sync-backup/syncthing/gui/default/assets/lang/lang-be.json

## Purpose
This JSON file provides Belarusian translations for part of the Syncthing web GUI. It maps English source strings to Belarusian strings, but has much lower coverage than the fully enabled language files in this subset.

## Important APIs, Types, And Functions
The file is a flat JSON object with 197 top-level keys, no empty string values, and no object-valued `theme` key. It follows the same English-key lookup model used by `angular-translate`. Belarusian is not present in the inspected `valid-langs.js`, so the normal locale selector does not advertise it.

## Control Flow
If the GUI loads language key `be`, these entries would satisfy matching translation lookups and fallback English would handle missing strings. Under the normal configured locale list, users cannot select `be`, so this file is currently a dormant or not-yet-enabled translation catalog.

## State And Persistence Behavior
The file persists generated translation content and no user state. The language asset README says these files are auto-generated from Weblate, so source-of-truth updates should happen through translation tooling.

## Dependencies And Integration Points
It depends on exact English source keys matching GUI templates and code. Placeholder-bearing entries use Angular interpolation syntax such as `{{name}}` and `{{count}}`. Because it is not in `valid-langs.js` or `prettyprint.js`, enabling it also requires updating language metadata.

## Risks And Edge Cases
Partial coverage means enabling this language would produce a mixed Belarusian/English UI. Absence of the nested `theme` translations may leave theme names in fallback language. Some entries remain visibly English, such as the observed `Upgrade To {{version}}`, which signals incomplete translation quality. Placeholder preservation must be checked before enabling.

## Test Signals
`jq` confirms valid JSON and 197 keys. Translation validation should compare key coverage against `lang-en.json`, check placeholder variable parity, and verify `be` stays absent from `valid-langs.js` until coverage and quality are acceptable.

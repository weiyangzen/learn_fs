# Research: sources/sync-backup/syncthing/script/weblatedl.go

## sources/sync-backup/syncthing/script/weblatedl.go

Purpose: translation downloader for Weblate-hosted Syncthing GUI translations.

Important APIs/types/functions: `stat`, `translation`, `reformatLanguageCode`, `saveValidLangs`, `saveLanguageNames`, `req`, and `loadValidLangs`.

Control flow: requires `WEBLATE_TOKEN`, loads currently valid languages, fetches component statistics, normalizes language codes, applies the same 75/95 percent acceptance thresholds, downloads every non-English translation file to `lang-<code>.json`, and rewrites `valid-langs.js` plus `prettyprint.js`.

State and persistence: writes language JSON and metadata files in the current working directory.

Dependencies and integration: Weblate API token auth, hosted.weblate.org endpoints, GUI language file format. Risks include no HTTP status validation, division by zero on bad stats, downloading low-completion non-English files even when not accepted into valid list, and regex JS array parsing. Test signal is generated file diff.

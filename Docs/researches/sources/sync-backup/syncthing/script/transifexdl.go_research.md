# Research: sources/sync-backup/syncthing/script/transifexdl.go

## sources/sync-backup/syncthing/script/transifexdl.go

Purpose: legacy translation downloader for Transifex-hosted GUI translations.

Important APIs/types/functions: `stat`, `translation`, `userPass`, `req`, `loadValidLangs`, `languageName`, `saveValidLangs`, and `saveLanguageNames`.

Control flow: requires `TRANSIFEX_USER` and `TRANSIFEX_PASS`, loads current valid languages, fetches resource stats, applies completion thresholds of 75 percent for currently valid languages and 95 percent for new languages, downloads each accepted non-English translation to `lang-<code>.json`, removes low-completion language files, and rewrites `valid-langs.js` and `prettyprint.js`.

State and persistence: writes/removes translation JSON and language metadata files in the current directory.

Dependencies and integration: Transifex API v2, basic auth, JSON, language metadata endpoint. Risks include division by zero if totals are zero, no HTTP status checks, credential requirements, and regex parsing of JS language arrays. Test signal is generated translation file diff.

# sources/sync-backup/git-lfs/tr/tr.go

Purpose: runtime translation locale initialization for Git LFS messages.

Important APIs/types/functions: package global `Tr`, `locales`, `findLocale`, `processLocale`, and `InitializeLocale`.

Control flow: finds locale from `LC_ALL`, `LC_MESSAGES`, then `LANG`; derives full and language-only options; initializes gotext locale/domain; looks up embedded base64 `.mo` data; decodes/parses first matching locale and adds translator.

State and persistence: global translator and embedded locale map; reads environment variables.

Dependencies and integration points: all translated messages in tools/tq use `tr.Tr.Get`; `trgen` generates data into `locales`.

Risks: global `Tr` mutation affects all packages. Invalid base64 data is skipped silently. Locale fallback only checks first matching embedded option.

Test signals: no direct tests in this subset.

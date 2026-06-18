# sources/sync-backup/kopia/app/notarize.mjs

## Purpose
Electron Builder `afterSign` hook that submits macOS KopiaUI builds for Apple notarization when explicitly enabled.

## APIs, Functions, and Control Flow
The module imports `dotenv/config`, `notarize` from `@electron/notarize`, and also imports `fs` and `crypto` though they are unused. It exports default async function `notarizing(context)`. The function returns immediately unless `context.electronPlatformName` is `darwin`. It then checks `process.env.KOPIA_UI_NOTARIZE`; if unset, it logs and skips notarization. Otherwise it builds the `.app` path from `appOutDir` and `context.packager.appInfo.productFilename`, logs progress every 30 seconds, and calls `notarize` with bundle id `io.kopia.ui` plus Apple API issuer, key id, and key path/content from environment variables.

## State, Persistence, and Dependencies
The hook depends on Electron Builder's context object and Apple notarization credentials. It may read `.env` through dotenv side effects. State persists externally in Apple's notarization service and in the signed app bundle after stapling/processing by the notarization library.

## Risks and Test Signals
`clearTimeout(timerId)` is used for an interval; it works in Node because timer clear functions are interchangeable, but `clearInterval` would be clearer. There is no `try/finally`, so a thrown notarization error can leave the interval active until process exit. The app packaging lane is the primary test signal; no standalone tests target this hook.

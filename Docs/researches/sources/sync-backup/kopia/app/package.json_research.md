# sources/sync-backup/kopia/app/package.json

## Purpose
Defines KopiaUI's Electron package metadata, runtime dependencies, build packaging configuration, and npm scripts.

## APIs, Control Flow, and Integration Points
The package is ESM (`type: module`) with main process entry `public/electron.js`. Runtime dependencies support auto-start integration, logging, local store, updater behavior, CLI argument parsing, semver handling, and UUID generation. Dev dependencies cover notarization, Electron, Electron Builder, Playwright E2E, asar, dotenv, concurrency helpers, and Prettier. Npm scripts expose Electron development, prebuilt start, Playwright E2E, Electron packaging, platform-specific packaging, directory builds, and formatting.

## State and Packaging Behavior
The `build` block configures product `KopiaUI`, app id `io.kopia.ui`, GitHub release publishing, packaged files, preload/resource copying, output directory `../dist/kopia-ui`, Windows NSIS/zip targets, macOS hardened runtime/entitlements/universal embedded server resource, Linux AppImage/deb/rpm targets, AppArmor profiles, and `afterSign: notarize.mjs`. Platform build sections embed the Kopia server binary from `../dist/kopia_*` into app resources.

## Risks and Test Signals
Packaging correctness depends on the top-level Makefile building the expected server binary paths before Electron Builder runs. The package includes `react-scripts` scripts but does not list `react-scripts` as a dependency in this file, suggesting legacy or unused HTML build scripts. Test signals are `npm run e2e`, `npm run prettier:check`, Electron Builder execution, and `npm audit --omit=dev`.

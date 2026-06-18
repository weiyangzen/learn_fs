# sources/sync-backup/kopia/app/Makefile

## Purpose
Builds and tests the Kopia Electron UI application. It handles npm dependency installation, development commands, E2E execution, Electron packaging, and formatting checks.

## APIs, Control Flow, and Integration Points
The file includes `../tools/tools.mk` to reuse pinned tool variables and retry behavior. `deps` creates `node_modules/.up-to-date` by running npm install/ci without audit, then runs `npm audit --omit=dev`. `electron_builder_flags` injects the version from `KOPIA_VERSION`, publish owner/repo, signing behavior, and platform architecture choices. Pull requests normally disable installer publishing and unset signing/notarization variables unless `FORCE_KOPIA_UI_SIGN` is set. `build-electron` depends on the embedded Kopia binary, node modules, public files, and resources, then runs `npm run build-electron`.

## State and Persistence
State includes `node_modules/.up-to-date`, `../dist/kopia-ui/.up-to-date`, packaged UI artifacts under `../dist/kopia-ui`, and Electron Builder side effects. Environment variables such as `CSC_LINK`, `CSC_KEY_PASSWORD`, `KOPIA_UI_NOTARIZE`, `NON_TAG_RELEASE_REPO`, `REPO_OWNER`, `GOOS`, and `KOPIA_UI_CURRENT_ARCH_ONLY` control build state and output shape.

## Risks and Test Signals
The Makefile carefully unsets signing secrets when inappropriate, but signing/notarization behavior remains sensitive to environment leakage. The dependency stamp can become stale if inputs are missed. Test signals include `npm audit --omit=dev`, Playwright E2E via `make e2e-test`, and Prettier checks.

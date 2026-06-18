# Research: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/pnpm-lock.yaml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008129`: lines 1-7316, `Docs/researches/chunks/subset-b-008129_research.md`
- `subset-b-008130`: lines 7317-9974, `Docs/researches/chunks/subset-b-008130_research.md`

## Chunk Research

### subset-b-008129: lines 1-7316

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/pnpm-lock.yaml lines 1-7316

## Purpose

This chunk is the first and larger part of the PNPM v9 lockfile for the Apache Ozone Recon web UI package at `hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web`. It records the deterministic dependency graph used to install, build, lint, test, mock, and run the React/Vite Recon frontend. The source package is private `ozone-recon` version `0.2.0` and declares `packageManager: pnpm@10.28.2` in `package.json`, while this lockfile uses `lockfileVersion: '9.0'`.

The covered lines include the global PNPM settings, the root importer, the full `packages:` catalog, and the beginning of the `snapshots:` graph through `is-glob@4.0.3`. Later lockfile lines continue the remaining snapshot resolutions.

## Structure And Important Records

- `settings.autoInstallPeers: true` means PNPM resolves peer dependencies automatically when possible.
- `settings.excludeLinksFromLockfile: false` means linked dependencies are retained in the lockfile if present.
- `importers .` is the root workspace/package importer for the Recon webapp. It pins top-level runtime dependencies and dev dependencies to exact resolved versions.
- `packages:` is the package metadata catalog. Each key is a package/version, optionally with peer context in later snapshot keys. Entries record integrity hashes, binary availability, Node engine constraints, OS/CPU/libc filters, peer dependency contracts, optional peer metadata, and deprecation notes.
- `snapshots:` starts at line 4700. Snapshot records bind concrete package instances to their resolved dependency trees, including peer expansions such as `antd@4.10.3(react-dom@16.14.0(react@16.14.0))(react@16.14.0)`.

This file does not define application APIs, functions, or types. Its "API surface" is the package manager contract consumed by `pnpm install`, `pnpm build`, `pnpm test`, `pnpm e2e`, and any Maven/CI wiring that builds the Recon web assets.

## Root Dependency Profile

The root importer describes an older React 16 UI coupled to a modernized Vite test/build stack:

- UI framework: `react@16.14.0`, `react-dom@16.14.0`, `antd@4.10.3`, `@ant-design/icons@4.8.3`, and a large `rc-*` Ant Design component family.
- Routing and forms/selects: `react-router@5.3.4`, `react-router-dom@5.3.4`, `react-select@3.2.0`.
- Visualization: `ag-charts-community@7.3.0`, `ag-charts-react@7.3.0`, `echarts@5.6.0`, and `zrender@5.6.1`.
- Data and formatting: `axios@1.16.0`, `filesize@6.4.0`, `pretty-ms@5.1.0`, `moment@2.30.1`, `classnames@2.5.1`.
- Markdown rendering: `react-markdown@8.0.7`, `remark-gfm@3.0.1`, and unified/micromark/mdast/hast dependencies.
- Styling/build-time CSS: `less@3.13.1`, `@fontsource/roboto@4.5.8`.
- TypeScript: `typescript@4.9.5` with React 16-era type packages.

Dev tooling in this chunk includes `vite@4.5.14`, `@vitejs/plugin-react-swc@3.11.0`, `vitest@1.6.1`, `jsdom@24.1.3`, `@playwright/test@1.60.0`, Testing Library packages, ESLint 7 plus TypeScript/React/import/promise/prettier plugins, `json-server@0.15.1`, `msw@1.3.3`, `npm-run-all@4.1.5`, and `prettier@2.8.8`.

## Dependency Graph And Control Flow

The install/build control flow is data-driven:

1. PNPM reads the root importer and installs the exact versions from `packages:` and `snapshots:`.
2. Peer resolution threads React 16 and React DOM 16 through Ant Design, `rc-*`, Testing Library, chart wrappers, routers, and selects.
3. Vite uses Rollup and esbuild/SWC packages. Optional native packages are selected by the current platform using `os`, `cpu`, and `libc` constraints.
4. `@vitejs/plugin-react-swc` pulls `@swc/core@1.15.18`, which in turn lists optional platform-specific SWC binaries.
5. `vite@4.5.14` depends on Rollup and esbuild, while the lockfile also contains `vite@5.4.21` as a transitive/peer-related package instance for other tooling context.
6. `vitest@1.6.1` uses `vite-node`, `@vitest/*`, `chai`, `jsdom`, `pretty-format`, `tinyspy`, and Node 18+ supporting packages.
7. Playwright is locked as `@playwright/test@1.60.0`, `playwright@1.60.0`, and `playwright-core@1.60.0`.
8. Mock API/dev support flows through `json-server`, `express`, `lowdb`, `request`, `method-override`, `morgan`, `cors`, and URL rewrite middleware.

The lockfile itself has no runtime branches, but package selection has implicit branch behavior through optional dependencies and platform filters. For example esbuild, Rollup, SWC, and `unrs-resolver` publish many platform-specific packages; only the compatible optional package should be installed for a given host.

## State And Persistence Behavior

The lockfile is persistent build state. It captures:

- Exact resolved versions for semver ranges in `package.json`, such as `^16.8.6` resolving to `react@16.14.0` and `~4.10.3` resolving to `antd@4.10.3`.
- Integrity hashes for supply-chain verification.
- Peer dependency resolutions, including nested peer contexts for React, React DOM, ESLint, TypeScript, Vite, Less, jsdom, and Testing Library.
- Optional platform packages that must remain present in the graph for cross-platform installs.
- Deprecation metadata for transitive packages.

No application state, Recon server state, browser local storage, or backend persistence appears in this file. Changing it changes install reproducibility and can indirectly change build output, test behavior, bundle size, and vulnerability surface.

## Integration Points

- `package.json` scripts consume this graph: `vite --port=3000`, `vite build`, `vitest`, `playwright test`, `json-server --watch api/db.json ... --port 9888`, `npm-run-all --parallel mock:api start`, and ESLint/Prettier commands.
- The React app integrates with Ozone Recon APIs through `axios`; mock API development is represented by `json-server` and `msw`.
- Ant Design 4 integration is broad: `antd` snapshots enumerate many `rc-*` packages for forms, menus, trees, selects, tables, upload, tabs, dialogs, pickers, sliders, pagination, notification, resize observers, virtual lists, and motion.
- Charting integration spans AG Charts React bindings and ECharts/ZRender.
- Markdown integration spans `react-markdown`, `remark-gfm`, `remark-parse`, `remark-rehype`, unified, micromark, mdast, hast, and unist utilities.
- Test integration spans Testing Library for React 16, jsdom for DOM emulation, Vitest for unit tests, and Playwright for browser tests.
- Lint integration spans ESLint 7, `@typescript-eslint` 5, React/import/promise/prettier plugins, and TypeScript resolver packages.

## Compatibility Notes

- Runtime UI dependencies are React 16-era. Testing Library React is locked to `12.1.5`, whose peer range is `<18.0.0`, matching the app.
- Several dev packages require Node 18 or newer: `@playwright/test@1.60.0`, `jsdom@24.1.3`, `vitest@1.6.1`, `vite-node@1.6.1`, `@inquirer/external-editor@1.0.3`, modern `@csstools/*`, `data-urls@5.0.0`, and `whatwg-*` packages. Vite 4 itself supports older Node, but the full dev/test graph effectively requires a newer Node runtime.
- `eslint@7.32.0` is deprecated and no longer supported, but the TypeScript ESLint packages are resolved against it.
- `@types/node@25.3.5` is much newer than `typescript@4.9.5` and the React 16 type set. This may be intentional for current Node APIs, but it is a type-compatibility risk if TypeScript 4.9 cannot parse or model future Node type declarations.
- `less@3.13.1` is older and runs under broad Node support, but modern Vite/plugin packages may exercise CSS handling through newer PostCSS and CSS parser dependencies.

## Notable Risks

- Supply-chain drift risk is concentrated here: edits to versions or integrity fields can change all downstream web build artifacts even if source code is unchanged.
- Deprecated transitive packages appear in the covered chunk, including `eslint@7.32.0`, `request@2.88.2`, `rimraf@3.0.2`, `glob@7.2.3`, `inflight@1.0.6`, `@humanwhocodes/config-array`, `@humanwhocodes/object-schema`, `@xmldom/xmldom@0.8.11`, and `uuid@3.4.0`.
- `@xmldom/xmldom@0.8.11` is marked in the lockfile as having critical issues. It is pulled through MSW/interceptor-related tooling, so exposure is likely test/dev, but it should still be tracked.
- `json-server@0.15.1` brings older Express/request/lowdb-era dependencies and should be treated as development-only.
- The graph mixes old UI packages with newer build/test packages. Upgrades can fail through peer expectations, React 16 compatibility, or Node engine constraints.
- Optional native package coverage is large. Removing apparently unused optional packages from the lockfile can break installs on other OS/CPU/libc combinations.
- Because this chunk ends mid-`snapshots`, analysis of the complete realized dependency tree must be reconciled with later chunks before producing a final per-file report.

## Test Signals

Useful validation after lockfile changes includes:

- `pnpm install --frozen-lockfile` in the Recon webapp directory to confirm the importer, package catalog, snapshots, peer contexts, and integrity hashes are self-consistent.
- `pnpm build` to verify Vite, SWC, Less, React 16, Ant Design 4, charting, markdown, and TypeScript all resolve together.
- `pnpm test` to validate Vitest, jsdom, Testing Library React 12, and MSW-related test dependencies.
- `pnpm e2e` to validate Playwright installation and browser-test dependency resolution.
- `pnpm lint` to catch ESLint 7, TypeScript parser, React plugin, import resolver, and Prettier plugin compatibility.
- For dependency/security work, compare `pnpm audit` results with the known deprecated or critical packages above, while separating dev-only risk from runtime bundle risk.

### subset-b-008130: lines 7317-9974

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/pnpm-lock.yaml lines 7317-9974

## Scope And Purpose

This chunk covers lines 7317-9974 of the `pnpm-lock.yaml` for the Apache Ozone Recon web application. The file is a `lockfileVersion: '9.0'` lockfile generated for `pnpm@10.28.2`; the importer at the top of the file declares a private React/Vite package named `ozone-recon`. The assigned range is in the lockfile's `snapshots:` section, not in the `packages:` metadata section or the application source tree.

These lines define 540 resolved package snapshot records from `is-negative-zero@2.0.3` through `zwitch@2.0.4`. Snapshot records are the dependency graph pnpm uses after package resolution: they record the concrete transitive dependency edges, peer-qualified package identities, optional dependency edges, and transitive peer dependency notes needed to recreate the same `node_modules` layout. The chunk is therefore build and supply-chain infrastructure for the Recon UI, not executable application logic.

The importer ties this graph to the Recon UI's direct dependencies: React 16, React DOM 16, Ant Design 4, React Router 5, React Select 3, ECharts, AG Charts, Axios, Less, Moment, `react-markdown`, `remark-gfm`, TypeScript, Vite, Vitest, Playwright, Testing Library, MSW, `json-server`, ESLint, Prettier, and related tooling.

## Important APIs, Types, And Functions

No JavaScript or TypeScript APIs, types, classes, or functions are declared by this chunk. The important "interfaces" are pnpm lockfile keys and the package-level APIs made available to the rest of the source tree when pnpm installs this graph:

- Snapshot keys such as `react-dom@16.14.0(react@16.14.0)` and `rc-table@7.12.5(react-dom@16.14.0(react@16.14.0))(react@16.14.0)` encode resolved package instances plus peer dependency bindings. This is critical for React libraries because many packages in the chunk are peer-bound to the single React 16 runtime.
- `dependencies:` blocks define exact transitive edges. Examples include `vite@4.5.14` depending on `esbuild`, `postcss`, and `rollup@3.30.0`; `vitest@1.6.1` depending on `vite@5.4.21`, `vite-node`, Chai, Tinybench, Tinypool, and `@vitest/*`; and `json-server@0.15.1` depending on Express, LowDB, Morgan, Request, Yargs, and middleware packages.
- `optionalDependencies:` captures platform-specific or feature-optional packages. Examples in this chunk include `less@3.13.1` optional support packages, `rollup@3.30.0`/`rollup@4.59.0` native bindings and `fsevents`, `vite` optional `@types/node`/`less`/`fsevents`, `web-encoding` optional `@zxing/text-encoding`, and `unrs-resolver` platform bindings.
- `transitivePeerDependencies:` lists peer requirements that pnpm could not flatten into normal dependencies, such as `supports-color`, `encoding`, `bufferutil`, `utf-8-validate`, and style preprocessor peers used by Vite/Vitest.
- Empty snapshots such as `moment@2.30.1: {}` and `typescript@4.9.5: {}` mean the resolved package has no further dependency edges in this lockfile graph.

The package groups most relevant to the Recon app surface are:

- React runtime and UI libraries: `react@16.14.0`, `react-dom@16.14.0`, `scheduler`, `prop-types`, `react-is`, `react-transition-group`, `react-input-autosize`, `react-select`, and many Ant Design `rc-*` primitives including align, cascader, checkbox, collapse, dialog, drawer, dropdown, field form, image, input number, mentions, menu, motion, notification, overflow, pagination, picker, progress, rate, resize observer, select, slider, steps, switch, table, tabs, textarea, tooltip, tree, trigger, upload, util, and virtual list.
- Markdown and API-description rendering stack: `react-markdown@8.0.7`, `remark-gfm@3.0.1`, `remark-parse`, `remark-rehype`, `unified`, `vfile`, `mdast-util-*`, `micromark-*`, `unist-util-*`, `hast`/property/token helpers, and `zwitch`.
- Browser and testing DOM stack: `jsdom@24.1.3`, `parse5`, `nwsapi`, `cssstyle`, `rrweb-cssom`, `whatwg-url`, `whatwg-encoding`, `webidl-conversions`, `w3c-xmlserializer`, `symbol-tree`, `tough-cookie`, `ws`, and `xml-name-validator`.
- Build and test tools: `vite@4.5.14`, `vite@5.4.21`, `vite-node@1.6.1`, `vite-tsconfig-paths@3.6.0`, `vitest@1.6.1`, `rollup@3.30.0`, `rollup@4.59.0`, `magic-string`, `tinyglobby`, `picomatch`, `typescript@4.9.5`, `tsconfig-paths`, `tsutils`, `sucrase`, `prettier@2.8.8`, `table`, and `optionator`.
- Mock API and local development tooling: `json-server@0.15.1`, `lowdb`, `morgan`, `method-override`, `server-destroy`, `body-parser` transitive packages in adjacent chunks, `request@2.88.2`, `msw@1.3.3`, `node-fetch@2.7.0`, `strict-event-emitter`, `outvariant`, and `headers-polyfill`.
- CLI/process helpers: `npm-run-all`, `npm-run-path`, `cross-spawn` transitive helpers, `pidtree`, `shell-quote`, `ora`, `log-symbols`, `update-notifier`, `latest-version`, `package-json`, `yargs@14.2.3`, and `yargs@17.7.2`.

## Control Flow

The chunk has no runtime control flow by itself. Control flow is induced by tools that consume the lockfile:

1. `pnpm install` reads the importer and snapshot graph, resolves exact package instances, installs packages into pnpm's content-addressed store, and creates `node_modules` links that match the peer-qualified snapshot identities.
2. `pnpm start` or the package script `vite --port=3000` uses the locked Vite 4 path for the Recon development server. The snapshot graph fixes Vite's transitive Rollup, Esbuild, PostCSS, Less, and resolver dependencies.
3. `pnpm build` uses the same Vite 4 production build graph. Optional native Rollup packages may be selected according to the host platform, with JavaScript fallback/optional dependency behavior controlled by the lockfile.
4. `pnpm test` runs Vitest 1.6.1. In this graph Vitest is bound to Vite 5.4.21 and Vite Node 1.6.1 rather than the app's direct Vite 4.5.14 build dependency, so test execution can exercise a different Vite major than the production build path.
5. `pnpm e2e` uses Playwright 1.60.0, while `pnpm dev` runs `npm-run-all --parallel mock:api start`, starting the Vite dev server and the `json-server` mock API together.
6. Runtime bundling includes application imports of React, Ant Design, routing, charts, markdown rendering, date/size formatting, and selected utility packages. This chunk contributes many of those resolved transitive packages.

Within a pnpm install, the peer-qualified keys drive branching in the dependency graph. For example, all `rc-*` packages in this range are resolved against `react@16.14.0` and usually `react-dom@16.14.0`; `react-markdown@8.0.7` is resolved against `@types/react@16.8.15` and React 16; `msw@1.3.3` is resolved with `@types/node@25.3.5` and `typescript@4.9.5`; and `vitest@1.6.1` is resolved with `jsdom@24.1.3` and `less@3.13.1`.

## State And Persistence Behavior

The persistent state in this chunk is dependency state: exact package versions and their transitive edges. It is committed so build, test, and development environments resolve the same graph without floating semver decisions on every install.

The chunk also controls the shape of persistent/generated local artifacts outside git:

- pnpm's global store and project `node_modules` symlink layout are derived from these snapshot keys.
- Optional native packages for Rollup, `unrs-resolver`, `fsevents`, and related platform bindings are installed or skipped based on OS/CPU and optional dependency rules.
- `json-server` and `lowdb` are development-time tools for the mock API declared in `package.json`; their runtime data source is the app's `api/db.json` and route/middleware files, not this lockfile.
- `update-notifier` and `configstore` in the `json-server` dependency tree can write user-level notification state when those CLIs run outside CI, depending on package behavior and environment variables.
- `tough-cookie`, `jsdom`, `msw`, and `node-fetch` hold HTTP/cookie state during tests or mocked requests, but those are runtime library behaviors rather than lockfile state.

Because the lockfile pins versions, changes to this chunk are high-signal supply-chain changes. A one-line version drift can change bundler behavior, React peer resolution, testing DOM behavior, markdown parsing, or mock API behavior across the Recon web application.

## Dependencies And Integration Points

The chunk integrates with the source tree through the Recon web app's package scripts and imports:

- `package.json` declares `packageManager: pnpm@10.28.2`, so this lockfile is the authoritative dependency graph for normal installs.
- The app's `start`, `build`, and `serve` scripts consume Vite, Rollup, Esbuild, PostCSS, Less, and resolver packages locked here.
- The `test` script consumes Vitest, Vite Node, JSDOM, Chai, Tinybench, Tinypool, Testing Library dependencies from earlier chunks, and many DOM/URL/XML packages in this range.
- The `e2e` script consumes Playwright packages locked in this range.
- The `mock:api` and `dev` scripts consume `json-server`, `npm-run-all`, `lowdb`, Express middleware packages, Request, Yargs, and process helpers.
- React UI source imports rely indirectly on the locked `rc-*` component graph under Ant Design 4. These packages handle layout, popups, forms, tables, dropdowns, trees, tabs, pickers, upload controls, resize observation, virtual lists, and motion.
- Markdown rendering of Recon UI content relies on `react-markdown`, `remark-gfm`, `unified`, `micromark`, `mdast-util-*`, `unist-util-*`, and `hast` helpers locked in this range.
- ECharts depends on `zrender@5.6.1`, which appears near the end of the chunk and brings `tslib@2.3.0`.

The chunk also records integration edges to external package ecosystems: npm package names and versions, native optional package families for Rollup and `unrs-resolver`, Node/browser polyfill packages, and peer dependency conventions for React, TypeScript, Less, Node types, and optional WebSocket native accelerators.

## Risks And Edge Cases

- The app directly pins Vite 4.5.14, while Vitest is resolved through Vite 5.4.21 in this snapshot graph. That is intentional according to the lockfile, but it creates a split build/test toolchain where a test may pass under Vite 5 behavior while production bundling uses Vite 4.
- React is pinned to 16.14.0 with `@types/react@16.8.15`, while several modern packages in the graph are peer-compatible but newer than the original React 16 ecosystem. Peer-qualified snapshot keys should be preserved carefully to avoid accidental duplicate React installs or invalid hooks behavior.
- `json-server@0.15.1` pulls the deprecated `request@2.88.2` stack, including legacy packages such as `uuid@3.4.0`, `tough-cookie@2.5.0`, `oauth-sign`, and `sshpk`. This is development/mock tooling, but it is still part of the installed dependency graph.
- `update-notifier@3.0.1` is present through `json-server` and can introduce user-environment side effects or noisy network/update checks when CLI tools run outside CI.
- The lockfile includes broad optional native dependency families for Rollup 4 and `unrs-resolver`. Install behavior can vary by platform; CI should exercise the same platform family used for release builds.
- `jsdom@24.1.3` and several `@csstools` packages in other parts of the lockfile require modern Node versions. If the Maven/Ozone build environment uses an older Node runtime, install or test phases may fail even though the application code has not changed.
- Markdown parsing uses a large unified/micromark stack. Changes in this chunk can affect GFM table/task/autolink handling, sanitization-adjacent URL processing, and rendered Recon UI content without changing application code.
- The Ant Design 4 `rc-*` graph is sensitive to exact peer bindings. Upgrading one `rc-*` package independently through lockfile churn can break overlay positioning, table layout, form behavior, date picker behavior, or virtual list rendering.
- The lockfile records `axios@1.16.0` in the importer outside this chunk; this chunk includes supporting URL, proxy, and DOM/test packages. Dependency audits need to merge chunk-level findings with the final whole-file report, because security-relevant packages are distributed across multiple lockfile ranges.

## Test Signals

Useful verification signals for this chunk are dependency and webapp checks:

- Run `pnpm install --frozen-lockfile` in `hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web` to confirm the snapshot graph is internally consistent and no importer/lockfile drift exists.
- Run `pnpm build` to verify Vite 4, Rollup 3, Esbuild, Less, PostCSS, React, Ant Design, charts, markdown, and route bundling still work with the locked graph.
- Run `pnpm test` to verify Vitest 1.6.1 with Vite 5.4.21 and JSDOM 24 still matches the app's unit/integration test assumptions.
- Run `pnpm e2e` where browser dependencies are available to verify Playwright's locked version and the built/dev app still work end to end.
- Run `pnpm dev` or the two constituent scripts to verify `npm-run-all`, Vite dev server, `json-server`, LowDB-backed mock data, route rewrites, and mock pagination middleware start together.
- Run `pnpm lint` to exercise ESLint resolver/parser dependencies outside this chunk but affected by shared package graph state.
- Inspect the installed graph with `pnpm list react react-dom antd rc-table react-markdown remark-gfm vite vitest json-server msw --depth 2` to catch duplicate React instances, unexpected Vite version shifts, or peer-resolution changes.
- For supply-chain review, compare changes in this range with `pnpm-lock.yaml` package metadata above the snapshots section; snapshot-only changes should correspond to explicit package or peer dependency changes, not unexplained lockfile churn.

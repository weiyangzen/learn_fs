# sources/test-tools/syzkaller/dashboard/app/util_test.go

Purpose: central App Engine/dashboard test harness for the `dashboard/app` package. It creates isolated app instances, mocked time/email, API clients, HTTP helpers, datastore loaders, config patchers, Spanner test setup, and common assertions.

Important APIs and types: `Ctx`, `NewCtx`, `NewSpannerCtx`, DDL loading/sorting helpers, assertion helpers, `Close`, time/config mutation helpers (`advanceTime`, `setSubsystems`, `setCoverageMocks`, `setKernelRepos`, `setNoObsoletions`, `updateReporting`, `decommission*`, `setWaitForRepro`, `SetAIConfig`), HTTP helpers (`GET`, `AuthGET`, `POST`, `POSTForm`, `AuthPOSTForm`, `ContentType`, `httpRequest`), datastore loaders, email helpers, `apiClient`, `makeClient`, API polling helpers, `incomingEmail`, `createAIJob`, `initMocks`, request-context mapping, and config replacement helpers.

Control flow: `NewCtx` starts `aetest.NewInstance`, initializes clients with dashboard keys, registers an initial request, and sets mocked time to 2000-01-01. HTTP/API helpers register requests so app code can recover the active `Ctx` and mocked time. `Close` validates rendered pages, drains email and external report queues, renders AI job pages when needed, closes clients, unregisters context, and validates global config. `NewSpannerCtx` creates a unique fake Spanner DB URI and applies migrations loaded from `aidb/migrations`.

State and persistence: maintains per-test App Engine datastore instance, mocked time, email sink channel, optional context transformer for config/mocks, request ID to context map guarded by a mutex, and generated API clients. It reads/writes datastore entities indirectly through app handlers and loader helpers. It patches global functions in `initMocks` for time, email sending, and max crash count.

Dependencies and integration points: App Engine `aetest`, datastore, mail, dashboard API client, `dashapi`, Spanner admin test DB, coverage DB client, covermerger, email parser, subsystem service, AI DB, testify, and the package's HTTP `DefaultServeMux`.

Risks: tests are skipped when `dev_appserver.py` is unavailable unless CI-like env is set; this can hide coverage locally. Request-context mapping is global and must unregister to avoid cross-test contamination. `Close` performs broad invariant checks only when `transformContext == nil`, so tests using config transforms bypass some final rendering/drain checks. DDL splitting assumes semicolons only terminate statements. Global mock functions affect the whole package test process.

Test signals: this file enables most integration tests in the package. Failures here usually indicate test environment setup, config mutation, request registration, or harness-level cleanup issues rather than a single feature regression.

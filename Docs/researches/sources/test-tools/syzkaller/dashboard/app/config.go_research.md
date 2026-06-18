# sources/test-tools/syzkaller/dashboard/app/config.go

Purpose: central configuration schema, installation, defaulting, and validation for the dashboard application.

Important APIs and types: `GlobalConfig` defines app-wide access, ACLs, API clients, namespaces, email addresses, monitored inboxes, discussion email mapping, throttling, upload bucket, and default/dungeon namespace. `Config` defines per-namespace behavior for reporting, API clients, repositories, AI, KCIDB, subsystems, UI caching, coverage, repro export, obsoleting-related features, and manager metadata. Additional structs describe AI stages, clients, ACLs, coverage, subsystem reminders, obsoleting, reporting stages, kernel repos, CC, KCIDB, and throttling. `installConfig` validates and installs global config, then initializes email, HTTP, API, KCIDB, Batch, and coverage DB subsystems. `getConfig` supports test-time context override and optional immutability checks.

Control flow: `checkConfig` canonicalizes email blocklist entries, validates throttle shape, client names/keys, access-level hierarchy, obsoleting settings, default and dungeon namespaces, namespace configs, global client AI namespace defaults, discussion email uniqueness, monitored inbox regexes, and ACL items. Namespace validation fills defaults for display/similarity, default hooks, validates repos/reporting/subsystems/coverage/AI/KCIDB/managers, and builds repo graph constraints. Reporting validation walks stages backward to enforce nondecreasing access restrictions, moderation flags, daily limit bounds, non-last embargo rules, filter defaults, config validation, and JSON marshalability.

State and persistence behavior: config is stored globally in `configDontUse` after validation and is expected read-only. Some validation mutates config by filling defaults such as access levels, reporting display titles, AI debounce, subsystem reminder defaults, `NeedRepro`/`TransformCrash`, global client namespace lists, and obsoleting start period.

Dependencies and integration points: every dashboard subsystem reads `getConfig`. This file integrates with `dashapi`, AI workflow types, email canonicalization, subsystem service, validator package, vcs repo validation, reporting type implementations, HTTP/API initialization, Batch cron registration, KCIDB, and coverage DB initialization.

Risks: validation panics at startup, which is desirable for bad static config but risky for dynamically altered test configs. Defaulting mutates the installed object, so immutability checks need to account for post-validation state. `APIClient.AllowedNamespace` only checks membership and assumes empty lists were expanded during validation. Many subsystems rely on config access-level inheritance being correct.

Test signals: no dedicated test in this subset, but many tests use `NewCtx`, config overrides, and `checkConfig` indirectly. Email, coverage, dungeon, cache, and batch behavior all depends on these definitions.

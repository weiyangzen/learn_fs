# sources/object-store/minio/cmd/common-main.go

## Purpose
`common-main.go` contains process-wide startup plumbing shared by MinIO server modes: terminal/color setup, console UI configuration, CLI context construction, environment-file and secret handling, early/global env validation, DNS cache refresh, root credential loading, KMS connection, TLS certificate loading, and detached background contexts.

## Important APIs, Types, And Functions
`init` initializes logger behavior, color, gob registrations, retry policy, release metadata, and CI/orchestrator flags. `minioConfigToConsoleFeatures`, `buildOpenIDConsoleConfig`, and `initConsoleServer` translate MinIO runtime config into Console environment and server objects. `buildServerCtxt` reads CLI flags/config into `serverCtxt`; `handleCommonArgs` validates addresses and initializes global config/certs directories. `envKV`, `parsEnvEntry`, `minioEnvironFromFile`, `readFromSecret`, and `loadEnvVarsFromFiles` implement env-file and secret loading. `serverHandleEarlyEnvVars`, `serverHandleEnvVars`, `loadRootCredentials`, `autoGenerateRootCredentials`, `handleKMSConfig`, and `getTLSConfig` update global runtime state.

## Control Flow
Startup reads early browser settings, builds server context from flags or config files, applies common args, loads env files/secrets, validates env-derived URLs/domains/IPs/credential presence, then initializes credentials, KMS, TLS, Console, and DNS refresh as needed. Many invalid inputs call `logger.Fatal`, making this file part of MinIO's fail-fast boot boundary.

## State And Persistence Behavior
This file mostly mutates process globals and environment variables. It creates config/certs/CAs directories with `0700`, ignores permission errors for mounted Kubernetes-like paths, sets `CONSOLE_*` env vars, and loads TLS cert manager state. Secrets are read from direct paths or `/run/secrets/<name>` and trimmed.

## Dependencies And Integration Points
It integrates with MinIO CLI flags, Console API, IAM OpenID provider state, browser config, KMS/KES, certificate manager, DNS cache, global endpoint/domain state, auth credential validation, logger, and MinIO config env constants.

## Risks And Test Signals
Risks include broad global side effects, fatal exits that are hard to unit-test, env parsing that only supports simple `KEY=value`/`export KEY=value`, and address/port collisions. Tests in `common-main_test.go` cover secret trimming and env-file parsing for quotes, comments, malformed entries, and export/no-export forms; broader startup paths need integration coverage.

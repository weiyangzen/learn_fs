# sources/test-tools/syzkaller/syz-cluster/pkg/app/config.go

## Purpose
Application YAML config loader and validator.

## Important APIs, Types, and Functions
AppConfig, EmailConfig, SMTPConfig, DashapiConfig, Config, loadConfig, Validate methods, sender constants, and validation helpers.

## Control Flow
Config uses sync.Once to load /config/config.yaml, apply defaults, unmarshal YAML, and validate URL/email/sender shape.

## State and Persistence
Process-wide cached configuration; no database persistence.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.

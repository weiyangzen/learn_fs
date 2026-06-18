# sources/object-store/minio/cmd/server-startup-msg.go

Purpose: This file formats and prints MinIO startup output: banner, API endpoints, WebUI endpoints, root credentials when allowed, region, configured notification/lambda ARNs, CLI setup guidance, and docs link. It also normalizes displayed endpoint URLs by stripping standard ports in multi-endpoint output.

Important APIs and types: `getFormatStr` builds printf width strings. `printStartupMessage` orchestrates banner and startup sections. `isIPv6` detects IPv6 hosts. `stripStandardPorts` removes `:80` from HTTP and `:443` from HTTPS endpoint displays when multiple endpoints are present. `printServerCommonMsg`, `printObjectAPIMsg`, `printLambdaTargets`, `printEventNotifiers`, and `printCLIAccessMsg` print individual startup sections.

Control flow: `printStartupMessage` prints the distributed banner framing when needed, reports startup errors to console, prints the startup banner unless subnet is registered, strips standard API ports, prints common API/WebUI info, prints CLI access using the first endpoint, prints docs, and closes the distributed banner. Common message printing reads global active credentials, region, API endpoints, Console endpoints, browser flag, API root-access permission, terminal/color state, notification targets, and lambda targets.

State and persistence behavior: There is no persistence. The code reads global server state and emits to `logger.Startup` and sometimes `globalConsoleSys`. It may reveal root credentials on terminal output when anonymous/JSON modes are off and root access is permitted.

Dependencies and integration points: It integrates with startup bootstrap in `server-main.go`, `logger`, color handling, Console system, subnet registration state, global API/browser config, notification system, lambda target list, endpoint discovery helpers, and MinIO documentation links.

Risks: Startup output depends on global state and terminal detection, so behavior can differ under JSON logging, tests, consoles, or non-interactive services. Credential printing is intentionally gated but security-sensitive. `stripStandardPorts` leaves empty strings for skipped IPv6 entries when host is empty and multiple endpoints are processed, which callers must tolerate in joined output.

Test signals: `server-startup-msg_test.go` verifies standard-port stripping behavior and smoke-tests the printing functions after creating test config.

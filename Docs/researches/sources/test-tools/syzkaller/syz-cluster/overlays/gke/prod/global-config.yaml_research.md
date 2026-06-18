# sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/global-config.yaml

## Purpose
Production syz-cluster global configuration.

## Important APIs, types, and functions
YAML config sets `URL: https://ci.syzbot.org`, `parallelWorkflows: 15`, Lore archive names, email reporting via dashapi, support/credit/archive/moderation/report CC addresses, dashapi context prefix `ci`, kernel trees, and fuzz targets grouped by subsystem mailing lists and campaigns.

## Control flow
Application components load this config from `global-config`. Controller exposes trees, series tracker/reporter use Lore/email settings, workflows use fuzz target campaigns, and dashboard/report links use the configured URL.

## State and persistence behavior
No state directly, but it controls production interactions with external systems: dashapi, mailing lists, lore.kernel.org, kernel git remotes, GCS corpus URLs, and workflow concurrency.

## Dependencies and integration points
Integrates nearly every syz-cluster service: email reporter, series tracker, controller, workflow generator, reporter, dashboard URLs, and fuzz config. Depends on external kernel repositories and mailing-list conventions.

## Risks and edge cases
This file contains production routing and recipient lists; mistakes can spam public lists, miss maintainers, or run wrong workflows. `parallelWorkflows: 15` increases resource demand. External URLs and branches must remain valid.

## Test signals
No direct test. Production behavior and config parser tests elsewhere are the main validation paths.

# sources/test-tools/syzkaller/dashboard/app/aidb/entities.go

## Purpose

`aidb/entities.go` defines the Cloud Spanner entity structs and workflow/action constants for the AI subsystem. These types are used by `aidb/crud.go` for reflection-based select lists, Spanner struct inserts/updates, and by dashboard UI/API code for display and behavior decisions.

## Important types and constants

- Action constants: `ActionJobReview` (legacy), `ActionApprove`, `ActionReject`, and `ActionUnreject`.
- Workflow filter constants: `WorkflowAll` and `WorkflowNeedsModeration`.
- `ActiveWorkflow`, `Workflow`, and `Agent` model available agent workflows and last active times.
- `Job` models an AI job, including workflow type/name, namespace, bug linkage, external/manual bug ID, display description/link, lifecycle timestamps, code revision, assigned agent, args/results JSON, correctness, abort state, and optional parent reporting.
- `TrajectorySpan` mirrors `trajectory.Span` for storing ordered agent execution traces.
- `Journal` records user or external-source actions, details, errors, source IDs, and reporting linkage.
- `JobReporting` models external report state for a job and stage, including source, publication timestamps, upstream user, external ID, version, and creation time.
- `JobComment` stores external comments tied to a reporting, including subject, author, body URI, timestamp, own-email flag, processing state, and DKIM verification.
- `JobReporting.ExternalLink` converts lore report external IDs into lore thread URLs.

## State and persistence behavior

All structs are plain exported-field records so Spanner's struct mapping can persist and hydrate them. Nullable fields use Spanner null wrapper types to distinguish unset from zero values. `Job.Args`, `Job.Results`, and `Journal.Details` are JSON-valued fields; tests and API code depend on these maps carrying patch diffs, patch metadata, base commit overrides, review details, and iteration targets.

`JobReporting.ExternalLink` is the only behavior method in this file. It returns an empty string if no valid external ID exists, and currently only knows how to construct a link for `dashapi.AIJobSourceLore` using `lore.LinkToThread`.

## Dependencies and integration points

The types depend on `cloud.google.com/go/spanner`, `dashboard/dashapi`, `pkg/aflow/ai`, and `pkg/email/lore`. They are referenced by AIDB CRUD operations, AI API handlers, UI rendering, review history loading, and external report polling/command handling.

## Risks and edge cases

Because `crud.go` builds `SELECT` lists by reflecting visible fields, adding or renaming fields here requires corresponding Spanner schema migration and careful update of tests. The `ExternalLink` method is source-specific; new external integrations will need explicit link support or will display without links. Nullable wrappers must be used consistently to avoid confusing unset correctness, unset publication, and empty string values.

## Test signals

The entity definitions are indirectly covered by Spanner DDL migration tests, AI job tests, reporting tests, and review history assertions. `ExternalLink` behavior is exercised through report UI/link payload expectations where lore external IDs are used.

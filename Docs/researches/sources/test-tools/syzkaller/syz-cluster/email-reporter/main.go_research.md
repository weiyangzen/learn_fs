# sources/test-tools/syzkaller/syz-cluster/email-reporter/main.go

## Purpose
Entry point and concurrency orchestration for the email reporter process.

## Important APIs, types, and functions
`main` loads config, validates `EmailReporting`, creates an email sender, constructs `Handler`, optionally creates a Lore poller, and starts goroutines under `errgroup`. Constants define sender poll period of 30 seconds and fetcher poll period of 2 minutes. `runConsumerLoop` processes polled Lore emails with retry delays. `MakeLorePoller` builds a `lore.Poller` with own-email addresses, 48-hour lookback, and stdout debug tracing.

## Control flow
Three logical loops can run: Lore poller loop if `LoreArchiveURL` is configured, consumer loop over the buffered channel, and outgoing report polling loop. `errgroup.WithContext` ties cancellation together. Consumer retries non-terminal processing errors with 30s, 1m, and 5m delays, and stops retrying for own/unknown emails.

## State and persistence behavior
The process keeps only channel/loop state in memory. Durable state is in report APIs, controller APIs, sender backend, and Lore checkout on the mounted disk. A file-level comment states only one copy should run at the same time.

## Dependencies and integration points
Depends on `app.Config`, `emailclient.MakeSender`, default controller/reporter clients, Lore poller, debug tracer, and `Handler`. Deployment mounts `/lore-repo`, and Dockerfile installs `git` for poller operation.

## Risks and edge cases
No OS signal handling is implemented beyond a background context, so shutdown relies on process termination. `PollReportsLoop` logs errors and continues forever. The retry loop condition uses `attempt < len(delays)`, which means the final attempt still logs retrying and indexes a valid delay only because the loop ranges over delays; the intended "give up" branch is effectively unreachable in the current range shape. A blocked consumer can back up the 16-slot channel.

## Test signals
`email_workflow_test.go` exercises `MakeLorePoller` and `ProcessPolledEmail`. `handler_test.go` covers handler behavior, but the concurrent main loop itself is not directly tested.

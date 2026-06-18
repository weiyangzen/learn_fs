# sources/test-tools/syzkaller/pkg/email/lore/poller.go

Purpose: `lore/poller.go` polls an LKML-style git archive, parses new messages, maintains ancestry metadata, and pushes root-resolved emails to consumers.

Important APIs/types/functions: `PollerConfig` configures repo directory, remote URL, tracer, own emails, lookback period, and test clock. `PolledEmail` carries parsed email, root message ID, and raw bytes. `Poller` stores repo handle, ancestor map, last processed commit, and initialization state. Main methods are `NewPoller`, `Poll`, `initialize`, `push`, `resolveRoot`, and `Loop`.

Control flow and state: first poll initializes by cloning/polling the archive and scanning all commit headers to populate `Message-ID -> In-Reply-To`. Subsequent polling fetches remote `master`, reads commits since `lastCommit` or within the lookback window, parses newest-to-oldest via `slices.Backward`, sanitizes future message dates to commit date, ignores missing message IDs, updates ancestor state, pushes to output unless an ancestry loop is detected, and advances `lastCommit`.

Dependencies and integration: it uses `vcs.NewLKMLRepo`, `ReadArchive`, `lore.Parse`, `email.ExtractInReplyTo`, `debugtracer`, contexts, and channels. `Loop` wraps `Poll` with a ticker and logs errors without exiting until context cancellation.

Risks: ancestor state is in-memory and can grow with archive size. `lastCommit` advances after each pushed/processed message, so crashes mid-batch may replay later messages. Poll errors are logged in `Loop` but suppressed. Tests cover initialization, lookback, root resolution, own-email parsing, loop detection, and date sanitization.

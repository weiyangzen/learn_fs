## sources/test-tools/syzkaller/pkg/lore-relay/relay.go

Purpose: orchestrates bidirectional relay between Lore mailing-list archive, email sender, and dashboard AI report APIs.

Important APIs/types/functions: `DashboardClient`, `Config`, `Relay`, `NewRelay`, `checkDKIM`, `Run`, `pollDashboard`, `PollDashboardOnce`, `PollLoreOnce`, `HandleIncomingEmail`, `replyError`, and `sendEmail`.

Control flow: `Run` starts Lore poller, dashboard poller, and email handler goroutines under an errgroup. Dashboard polling renders new reports, computes subject, To/Cc/In-Reply-To, sends email, and confirms publication. Lore polling handles incoming emails, optionally verifies DKIM domain, ignores unauthenticated commands, maps command/comment requests, retries dashboard calls with backoff, stays silent for untracked reports, and replies to command errors.

State and persistence: in-memory channel and backoff slice. External persistence occurs in dashboard state and sent email systems.

Dependencies and integration: integrates `lore.Poller`, `sender.Sender`, dashboard API, DKIM verification, debug tracer, and template rendering.

Risks: DKIM author parsing is simplistic. Handler goroutine reads from `emailChan` without ok check on close. Multiple commands are silently ignored. Backoff uses `time.After` per retry. Email send success must be confirmed to dashboard or reports can be re-polled.

Test signals: `relay_test.go` covers main flow, restart, errors, unsupported commands, and backoff behavior with mocks.

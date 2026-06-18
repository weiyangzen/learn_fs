# sources/test-tools/syzkaller/dashboard/app/discussion.go

Purpose: stores and summarizes external discussion threads related to dashboard bugs, especially lore/email discussions and patch threads.

Important APIs and types: `saveDiscussionMessage` converts a parsed incoming email into a `dashapi.Discussion` update, deciding whether to ignore, append to an existing thread, or create a new thread using `email.NewMessageAction`. `mergeDiscussion` creates or updates a `Discussion` datastore entity, merges bug associations, deduplicates messages, and updates per-bug summaries. `mergeDiscussionSummary` updates `Bug.DiscussionInfo` for a source. `DiscussionSummary.merge`, `Bug.discussionSummary`, `Discussion.addMessages`, `messageIDs`, `link`, `discussionByMessageID`, `discussionsForBug`, `getBugKeys`, and `unique` provide supporting behavior.

Control flow: incoming email saves first identify a parent discussion by `InReplyTo` if possible, then action rules determine thread ID/type. A cross-group transaction updates the discussion entity because bug associations can span multiple bugs. Per-bug summary updates are intentionally performed afterward in separate transactions to avoid App Engine entity-group limits.

State and persistence behavior: `Discussion` entities store source, type, subject, bug key string IDs, message metadata, and summary counters. `Bug` entities store source-specific summary records. Message storage deduplicates by ID, sorts by time, preserves the first message, and caps retained messages at 1500 while summaries continue to accumulate counts.

Dependencies and integration points: integrates with `dashapi.Discussion`, email parsing/action logic, lore link generation, bug lookup by reporting ID, datastore transactions, UI code that reads discussions for bug pages, and reporting email code that calls `saveDiscussionMessage`.

Risks: `mergeDiscussion` returns nil if `getBugKeys` fails, which intentionally ignores unknown bug IDs but can hide ingestion problems. Duplicate message IDs in multiple discussion entities become an error with a TODO to merge. Summary updates outside the main transaction can leave discussion and bug summary temporarily inconsistent if a later bug update fails.

Test signals: `discussion_test.go` covers multi-bug access, own/external message counts, unrelated discussion filtering, subdiscussion creation without original parent, patch-link discovery, bot reply ignoring, and message overflow retention.

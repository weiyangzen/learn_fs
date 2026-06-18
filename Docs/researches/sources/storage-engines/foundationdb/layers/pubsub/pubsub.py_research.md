# sources/storage-engines/foundationdb/layers/pubsub/pubsub.py

Purpose: This is the current SimpleDoc-backed FoundationDB PubSub layer in this subset. It models feeds, inboxes, subscriptions, and retroactive message delivery where an inbox can see historical messages from feeds it subscribes to.

Important APIs and types: Global SimpleDoc handles include `feeds`, `inboxes`, `messages`, and ordered index `feed_messages`. Transactional helpers implement feed/inbox creation, subscriptions, posting, listing, dirty-feed copying, subscription listing, clearing, and printing. `PubSub` wraps those helpers as methods on a database-bound object.

Control flow: Creating a subscription records the feed under `inbox.subs` and marks the feed dirty for that inbox. Posting prepends a message, sets its `fromfeed`, marks currently watching inboxes dirty, and clears the feed's watcher list. Reading inbox messages first copies messages from dirty feeds into `inbox.messages`, re-registers the inbox as watching those feeds, clears dirty markers, updates `latest_message`, then returns recent message values up to the limit.

State and persistence behavior: Persistent state is a SimpleDoc tree under `root.feeds`, `root.inboxes`, and `root.messages`. Inbox state includes subscriptions, dirty feeds, cached message IDs, and the latest message marker; feed state includes watching inboxes. Clearing wipes the SimpleDoc root.

Dependencies and integration points: It depends on `simpledoc` and its `OrderedIndex`, not raw FDB tuples directly. The bottom of the file embeds a random threaded sample workload using `fdb.api_version(22)` when run as `__main__`.

Risks: The embedded sample relies on globals `ps`, `random`, `threading`, and `time` only initialized in the main block. `get_inbox_subscriptions` accepts a limit but does not enforce it. Message ordering and `latest_message` comparisons depend on SimpleDoc child ordering and prepend ID semantics. Tests should cover retroactive subscriptions, dirty/watching transitions, repeated reads, limits, concurrent posts and reads, and `clear_all_messages` isolation.

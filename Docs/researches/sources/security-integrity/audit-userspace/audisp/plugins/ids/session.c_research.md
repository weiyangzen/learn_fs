# sources/security-integrity/audit-userspace/audisp/plugins/ids/session.c

Purpose: tracks active audit login sessions, their scores, origin address, kill flag, and account name.

Important APIs and data: exports lifecycle, traversal, add/find/delete/current access, and `add_to_score_session`. Sessions are stored in a global AVL tree keyed by session id.

Control flow: `new_session` allocates and initializes a session, then `add_session` inserts it, creates missing origin/account entries, and updates `cur`. Deletion removes the AVL entry and frees the account string. Scoring updates `cur` and increments score.

State and persistence: global process-local AVL tree and current pointer only. Session state is destroyed on logout, system lifecycle events, or process exit.

Dependencies and integration: uses `origin.c` to associate sessions with origins, `account.c` to track accounts, and model files for scoring.

Risks: `new_session` stores `acct ? acct : strdup("")`; when `acct` is NULL this can assign a newly allocated string, but when non-NULL it assumes ownership of a pointer created by the caller. `dump_session` prints `s->acct` directly and would be unsafe if NULL.

Test signals: create/find/delete duplicate sessions, account/origin side effects, and score threshold interactions through behavior model.

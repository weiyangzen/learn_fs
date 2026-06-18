## sources/security-integrity/audit-userspace/audisp/plugins/ids/account.c

Purpose: IDS account-state index keyed by account name.

It wraps an AVL tree in `accounts`, tracks count and current account, and provides init/destroy/new/add/find/delete/traverse/score APIs. Each `account_data_t` embeds `avl_t` first, owns a duplicated name, and carries a `karma` score. State persists in memory for the life of `audisp-ids` and is dumped via `traverse_accounts`. Dependencies are `avl`, IDS debug logging, and reactions hooks. Risks include global singleton state, no thread safety, allocation failure silently dropping new accounts, and score reaction placeholder currently doing nothing above threshold. Tests should cover duplicate add, delete, traversal, and karma increments.

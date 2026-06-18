# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/trust_notify.c

Purpose: This LDB module tracks changes to trust-related directory data and notifies `winbind_server` at successful transaction commit so winbind can reload trusted-domain data.

Important APIs, types, and functions: `struct trust_notify_private` holds a transaction-local `notify_winbind` flag. `trust_notify_has_watched_attrs` identifies changes to trust/crossRef attributes cached by winbind. `trust_notify_add`, `trust_notify_modify`, and `trust_notify_delete` decide whether to set the flag. Transaction hooks `trust_notify_start_trans`, `trust_notify_end_trans`, and `trust_notify_del_trans` reset, send, or clear notifications. `trust_notify_winbind_server` initializes an imessaging client, locates `winbind_server` with `irpc_servers_byname`, and sends `MSG_WINBIND_RELOAD_TRUSTED_DOMAINS`.

Control flow: Adds and modifies skip special DNs, check whether the incoming message contains watched attributes, set `notify_winbind`, then chain to the next module. Deletes skip special DNs, read the target object from the next module with recycled/internal/storage-format visibility, and set the flag if the object class is `trustedDomain` or `crossRef`. At transaction start or abort the flag is cleared. At transaction end, the module first commits downstream with `ldb_next_end_trans`; only on success does it send the reload message if the flag was set.

State and persistence behavior: The module persists no database state. Its only state is the private `notify_winbind` boolean scoped to a transaction. Notification delivery is best-effort: missing loadparm, imessaging initialization failure, no winbind server, or send failure does not roll back the already successful LDB transaction.

Dependencies and integration points: It depends on LDB module hooks, DSDB search helpers, Samba loadparm, imessaging/IRPC, server ID lookup, and the winbind reload message type. It integrates with trustedDomain, crossRefContainer, and crossRef attribute changes that affect winbind's trust cache.

Risks: There is an apparent bug in `trust_notify_modify`: it calls `trust_notify_has_watched_attrs(req->op.add.message)` inside the modify handler, where `req->op.mod.message` is expected. That wrong union arm can produce incorrect behavior or unsafe access for modify requests. Notification is also not retried and only targets the first found `winbind_server`.

Test signals: No dedicated tests are included in this subset. Useful coverage would assert that add/modify watched attributes set the flag, non-watched changes do not, deletes of trustedDomain/crossRef objects notify, transaction abort clears the flag, and successful commit sends exactly one reload message. A modify test should specifically catch the wrong request union arm.

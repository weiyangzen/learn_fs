# sources/user-network-fs/samba/source4/kdc/kpasswd-helper.c

## Purpose
`kpasswd-helper.c` provides helper routines for Samba's Kerberos password-change service. It formats kpasswd protocol result blobs, maps Samba password-change failures to Kerberos kpasswd errors, writes password changes through SAMDB transactions, and rejects inappropriate TGT-based authorization.

## Important APIs, Types, And Functions
`kpasswd_make_error_reply` creates a two-byte kpasswd status plus UTF-8 message blob. `kpasswd_make_pwchange_reply` maps `NTSTATUS` and `samPwdChangeReason` values to kpasswd success, access-denied, soft-error, or hard-error replies. `kpasswd_samdb_set_password` opens SAMDB as the authenticated session, resolves target user or service principal DN, and calls `samdb_set_password`. `kpasswd_check_non_tgt` enforces that the ticket to kpasswd is not a TGT.

## Control Flow
Password setting opens `samdb_connect`, logs the actor domain/account/SID and target principal, starts an LDB transaction, cracks the target principal according to user-vs-service mode, calls `samdb_set_password` with `DSDB_PASSWORD_RESET`, commits on success, and cancels on failure. Reply generation distinguishes no-such-user/access-denied, domain password policy restriction reasons, generic failures, and success.

## State And Persistence Behavior
This file performs real persistent changes through `samdb_set_password` inside an LDB transaction. On failure it cancels the transaction. It also returns domain password policy information (`samr_DomInfo1`) and reject reasons for user-facing kpasswd replies.

## Dependencies And Integration Points
It depends on Kerberos kpasswd constants, SAMR NDR types, SAMDB password APIs, Samba auth session information, loadparm/event contexts, and principal-cracking helpers. It is called by the kpasswd service shared by Heimdal and MIT startup paths.

## Risks
The transaction boundary around password changes is critical. Reply formatting must avoid length overflow and handle UTF-8 conversion correctly. Error strings can reveal operational details but are standard protocol feedback. `kpasswd_check_non_tgt` prevents a TGT from being used directly as the kpasswd service ticket, an important protocol authorization check.

## Test Signals
Tests should cover successful password change, no such user, access denied, password too short, complexity failure, password history, generic password restriction, transaction commit failure, service-principal resolution, user-principal resolution, and TGT rejection.

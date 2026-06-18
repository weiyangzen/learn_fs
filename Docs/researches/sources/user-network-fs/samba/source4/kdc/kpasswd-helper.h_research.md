# sources/user-network-fs/samba/source4/kdc/kpasswd-helper.h

## Purpose
`kpasswd-helper.h` declares the helper API used by Samba's kpasswd service to format replies, set passwords, and validate ticket type.

## Important APIs, Types, And Functions
It declares `kpasswd_make_error_reply`, `kpasswd_make_pwchange_reply`, `kpasswd_samdb_set_password`, and `kpasswd_check_non_tgt`. The password-setting API takes event/loadparm/session context, service-principal mode, target principal name, password blob, and output reject/domain policy details.

## Control Flow
Callers validate the ticket with `kpasswd_check_non_tgt`, attempt password change with `kpasswd_samdb_set_password`, then convert the resulting `NTSTATUS` and policy reason to a kpasswd reply blob with `kpasswd_make_pwchange_reply`.

## State And Persistence Behavior
The header itself stores no state. The implementation can persist password changes through SAMDB and returns policy metadata by output pointer.

## Dependencies And Integration Points
The declarations connect kpasswd service code to Samba auth sessions, loadparm, tevent, SAMR password policy types, Kerberos error codes, and `DATA_BLOB` reply conventions.

## Risks
Callers must pass the correct `is_service_principal` mode and preserve output pointer ownership expectations. Incorrect ticket-type validation or status-to-reply mapping would affect kpasswd authorization and client behavior.

## Test Signals
Build coverage plus kpasswd end-to-end tests for success, policy rejection, authorization failure, and TGT rejection are the primary signals.

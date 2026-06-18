# sources/test-tools/syzkaller/syz-cluster/pkg/emailclient/sender.go

## Purpose
Email sender factory for SMTP and dashapi backends.

## Important APIs, Types, and Functions
Sender type, MakeSender, newSMTPSender, SMTP secret constants, queryCredentials, querySecret, TestEmailConfig.

## Control Flow
Switches on app.EmailConfig.Sender; SMTP reads GCP secrets and dashapi builds sender config directly.

## State and Persistence
Reads external secrets and sends through external services; no app DB writes.

## Dependencies and Integration Points
Integrates app.EmailConfig, syzkaller email sender backends, GCP project/secret lookup, and SMTP/dashapi services.

## Risks and Edge Cases
Risks include secret lookup retries without backoff, runtime GCP dependency, and assuming config was validated earlier.

## Test Signals
No direct unit test here; app config validation and email/report tests cover adjacent behavior.

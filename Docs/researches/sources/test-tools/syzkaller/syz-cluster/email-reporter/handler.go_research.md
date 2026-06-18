# sources/test-tools/syzkaller/syz-cluster/email-reporter/handler.go

## Purpose
Implements email reporter business logic: polling pending reports, sending moderation/upstream emails, recording outgoing replies, and processing incoming `#syz` commands from email or Lore.

## Important APIs, types, and functions
`Handler` owns reporter identity, `api.ReporterClient`, controller `api.Client`, email configuration, and an `emailclient.Sender`. Sentinel errors are `ErrOwnEmail` and `ErrUnknownReport`. `PollReportsLoop` repeatedly calls `PollAndReport`. `PollAndReport` fetches the next report and calls `report`. `report` confirms the report before sending, renders email body via `pkg/report`, sends through the configured sender, and records the sent message ID when available. `IncomingEmail` interprets supported commands. `ProcessPolledEmail` records a polled reply for idempotency and delegates to `IncomingEmail`. `stripContextPrefix` normalizes dashapi context-prefixed bug IDs.

## Control flow
Outgoing flow starts with `GetNextReport`; if a report exists, `ConfirmReport` is called before rendering/sending to reduce duplicate-send risk. Moderation reports go to the moderation list with archive CC and a moderation subject prefix. Non-moderation reports are sent to report CCs, include archive/report CC, optionally include configured CI name in the subject, and preserve `InReplyTo`. Incoming flow rejects emails without bug IDs and ignores own non-forwarded emails. Supported commands are upstream, invalid, and argument-free `#syz test` with an attached patch; unsupported commands produce a reply explaining non-support. Processing polled email first calls `RecordReply`; unknown or already-seen replies are stopped before command execution.

## State and persistence behavior
Report confirmation, upstreaming, invalidation, job submission, and reply recording are persisted through reporter/controller APIs. The handler itself is stateless except for injected clients/config. The outgoing sender may or may not return a message ID; only non-empty IDs are recorded.

## Dependencies and integration points
Depends on `pkg/email`, `pkg/email/lore`, `pkg/email/sender`, `pkg/api`, `pkg/app`, `pkg/emailclient`, and `pkg/report`. Integrates with reporter server for report lifecycle, controller for patch-test job submission, dashapi/SMTP sender configuration, and Lore poller reply threading.

## Risks and edge cases
Confirm-before-send avoids duplicate emails but can drop a report if rendering or sending fails after confirmation. The TODO explicitly notes retry ambiguity when send errors may still have delivered mail. `IncomingEmail` processes commands sequentially and keeps only one reply string, so multiple commands can overwrite earlier unsupported-command replies. `#syz test` with args is rejected and patchless tests reply to the author. Only the first bug ID is used. Own forwarded emails are allowed to support dashboard forwarding.

## Test signals
`handler_test.go` covers moderation/upstream flow, invalidation, unsupported commands, own-email filtering, forwarded own email, and `#syz test` job flow/error cases. `email_workflow_test.go` covers Lore idempotency and reply identification.

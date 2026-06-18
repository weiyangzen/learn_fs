## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/main.go

This utility loads syz-cluster config, verifies email reporting is configured, constructs an email sender, and sends a fixed test message to the moderation list. It is intended for deployment/config validation rather than application flow.

State is external to the email provider; no local persistence. Dependencies are `app.Config`, `emailclient.MakeSender`, and syzkaller email sender types. Risks include a hard-coded message body typo, fatal behavior on any config/sender error, and no explicit error handling of the final `emailSender` call return because the sender function has no checked return in this usage.

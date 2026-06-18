## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/Dockerfile

This Dockerfile packages the `send-test-email` tool. It copies the built binary from the common builder image into Alpine as `/bin/send-email` and uses it as entrypoint.

Integration is with the send-test-email job. Risks are Alpine compatibility and root execution by default.

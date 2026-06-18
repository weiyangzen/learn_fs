## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/job.yaml

This Kubernetes `Job` sends one test email using the `send-test-email` image. It runs with `gke-email-reporter-ksa`, mounts global config at `/config`, imports `global-config-env`, has no retries, and keeps completed job records for one day.

Integration is with email reporting configuration and service-account permissions. Risks include no retry on transient email provider failures and fixed moderation-list recipient controlled by config.

# sources/test-tools/syzkaller/syz-agent/k8s/overlays/prod-lore/lore-relay-config.yaml

Purpose: production configuration for syz-lore-relay.

Important APIs/types/functions: YAML fields for dashboard credentials, lore URL, bot identities, archive email, DKIM verification, docs link, and SMTP secret references.

Control flow: loaded by lore-relay config parser, which resolves GCP secrets and constructs dashboard/lore/SMTP clients.

State and persistence: points relay at lore checkout PVC via deployment; config itself is a ConfigMap.

Dependencies and integration points: depends on GCP secrets and external SMTP service.

Risks: config contains operational email identities; wrong values can send mail from/to the wrong addresses or fail DKIM policy.

Test signals: relay startup and optional `-test-email`.

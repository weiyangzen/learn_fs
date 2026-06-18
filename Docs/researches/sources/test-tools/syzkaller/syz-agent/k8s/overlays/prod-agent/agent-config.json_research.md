# sources/test-tools/syzkaller/syz-agent/k8s/overlays/prod-agent/agent-config.json

Purpose: production syz-agent config for syzbot AI workflows.

Important APIs/types/functions: JSON config with GCP secret references, 350GB cache, linux/amd64 qemu target, and linux/arm64 GCE target.

Control flow: loaded by syz-agent; secret fields are resolved by `gcpsecret`. The arm64 VM uses `gcs_path` secret resolution inside nested VM config.

State and persistence: large cache is stored under the agent workdir; VM images/configs are static paths in the container.

Dependencies and integration points: requires GCP secret access, dashboard `https://syzbot.org`, qemu/KVM for amd64, and GCE for arm64.

Risks: secret resolution or missing kernel config/image paths blocks startup. Target count/VM counts influence cloud cost and queue capacity.

Test signals: config load, agent logs, dashboard job acceptance, and successful flow execution.

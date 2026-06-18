## sources/test-tools/syzkaller/syz-cluster/workflow/triage/workflow-template.yaml

This Argo template runs `triage-action`. An init container clones `/kernel-repo` into `/workdir` using a reference clone and writes a commit graph. The main container runs as UID/GID 10000, reads the cloned repo, writes `/output/result.json`, and exposes it as the `result` output parameter. It retries up to three times with five-minute backoff.

Integration points are the base kernel repo PVC `base-kernel-repo-pv-claim`, workflow `session-id`, and triage-action image. Risks include PVC freshness, git clone cost, privileged-ish filesystem ownership issues handled with `HOME`, and failure if output JSON is not produced. It requires `GIT_DISCOVERY_ACROSS_FILESYSTEM=1` for git behavior across mounts.

# sources/test-tools/kdevops/playbooks/ai_uninstall.yml

Purpose: uninstalls AI benchmark components from baseline/dev hosts.

Important APIs/types/functions: targets `baseline:dev` and invokes role `ai_uninstall`.

Control flow: delegates all teardown logic to the uninstall role.

State/persistence behavior: expected to remove packages, containers, configuration, or runtime components while possibly preserving benchmark data depending on role policy.

Dependencies/integration: paired with AI install/setup/test playbooks and role variables.

Risks/test signals: wrapper does not expose safeguards itself; destructive scope must be reviewed in the role. Test signals are absent services/packages after run and idempotent repeated uninstall.

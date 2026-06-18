# sources/test-tools/kdevops/playbooks/ai_results.yml

Purpose: collects and analyzes AI benchmark results from baseline/dev hosts.

Important APIs/types/functions: targets `baseline:dev` and invokes role `ai_collect_results`.

Control flow: all behavior is delegated to the role, which is expected to fetch, aggregate, or summarize AI benchmark artifacts.

State/persistence behavior: writes local or shared result artifacts derived from remote benchmark outputs.

Dependencies/integration: integrates with AI benchmark roles, Milvus result JSON format, and source-tree result directories.

Risks/test signals: role-only wrapper has little validation itself. Test signals are fetched result files, generated summaries, and idempotent repeated collection.

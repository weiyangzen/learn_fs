<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/call_agent.py -->
# sources/user-network-fs/blobfuse2/scripts/call_agent.py

## Purpose
GitHub workflow helper that responds to issues or discussions using an Azure AI Foundry agent grounded by optional DeepWiki context and local repository documentation snippets.

## Important APIs, Types, and Functions
Top-level code loads `GITHUB_EVENT_PATH`, detects issue versus discussion events, and supports a `DRY_RUN` fallback. `query_deepwiki` invokes `deepwiki_query.py`. `search_local_docs` ranks configured documentation files by keyword overlap. The script builds a prompt, calls `client.responses.create`, strips summary/source sections with regexes, prepends an AI disclaimer, optionally summarizes/truncates for GitHub limits, and posts through REST issue comments or GraphQL discussion comments.

## Control Flow and State
State comes from GitHub event JSON and environment variables including `DEEPWIKI_REPO`, `FOUNDRY_BASE_URL`, `FOUNDRY_API_VERSION`, `GITHUB_TOKEN`, and `DRY_RUN`. The script reads local docs but writes no repository files. It posts network side effects to GitHub unless in dry-run mode.

## Dependencies and Integration Points
Depends on `requests`, `openai`, `azure.identity`, the GitHub REST/GraphQL APIs, local docs, and the sibling `deepwiki_query.py`. It integrates with GitHub Actions event payloads.

## Risks and Edge Cases
Top-level execution makes import unsafe. It trusts environment-provided endpoints and tokens. Regex stripping may remove useful answer content. Local doc search is simple keyword matching and can miss relevant sections. Generated answers are explicitly non-authoritative. Discussion GraphQL errors are handled, but many OpenAI/Azure errors before posting are not.

## Test Signals
`DRY_RUN=true` prints target URL, question, and answer for validation without posting. Real workflow success is a posted comment URL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/call_agent.py -->

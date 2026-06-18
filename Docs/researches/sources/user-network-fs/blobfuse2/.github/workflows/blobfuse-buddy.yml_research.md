# sources/user-network-fs/blobfuse2/.github/workflows/blobfuse-buddy.yml

## Purpose
This workflow posts AI-generated replies to newly opened issues or discussions, with a manual-dispatch mock mode for testing the reply path.

## Important APIs, Types, and Functions
It uses `azure/login@v3` with OIDC, `actions/setup-python@v6`, Python packages `openai`, `azure-identity`, `requests`, `mcp`, `httpx`, and `python-dotenv`, and repository script `scripts/call_agent.py`. It writes a `mock_event.json` payload for manual tests.

## Control Flow
The workflow triggers on `issues.opened`, `discussion.created`, or manual dispatch. It checks out code, authenticates to Azure, sets Python 3.11, installs dependencies, optionally synthesizes a GitHub event payload from workflow inputs, then runs `scripts/call_agent.py` with event path, GitHub token, Azure AI Foundry endpoint, API version, repository name, and a dry-run flag for manual dispatch.

## State and Persistence Behavior
Manual dispatch creates `mock_event.json` in the workspace. Production runs can write issue or discussion comments through the GitHub token. Azure login state is ephemeral in the runner.

## Dependencies and Integration Points
It integrates GitHub issue/discussion events with Azure AI Foundry through OIDC secrets `AZURE_MCP_CLIENT_ID`, `AZURE_MCP_TENANT_ID`, and `AZURE_MCP_SUBSCRIPTION_ID`. The real behavior is concentrated in `scripts/call_agent.py`.

## Risks and Edge Cases
The workflow grants write permission to issues and discussions, so prompt-injection handling and script safeguards matter. The manual mock hardcodes default title/body values before reading inputs. The API version is a future preview string, so availability and SDK compatibility are sensitive.

## Test Signals
Signals include manual dispatch dry-run output, successful Azure login, `scripts/call_agent.py` completing, and a real issue/discussion run producing an appropriate comment without exposing secrets.

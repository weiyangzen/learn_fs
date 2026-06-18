<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/askbuddy.py -->
# sources/user-network-fs/blobfuse2/scripts/askbuddy.py

## Purpose
Minimal manual smoke script for calling an Azure AI Foundry/OpenAI-compatible Blobfuse buddy endpoint.

## Important APIs, Types, and Functions
Creates an Azure bearer token provider with `DefaultAzureCredential` and scope `https://ai.azure.com/.default`, constructs an `OpenAI` client with a hard-coded Foundry application base URL and API version, calls `client.responses.create`, and prints `response.output_text`.

## Control Flow and State
The script executes top-level code only. It sends a fixed prompt about `direct-io` versus `disable-kernel-cache` and exits.

## Dependencies and Integration Points
Depends on `openai` Python SDK and `azure.identity`. Integrates with Azure AI Foundry and local Azure credential configuration.

## Risks and Edge Cases
The service URL and preview API version are hard-coded. No timeout, error handling, or environment override is provided. It will fail outside an authenticated Azure environment.

## Test Signals
Successful output validates local credentials and endpoint reachability, not Blobfuse2 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/askbuddy.py -->

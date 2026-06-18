# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentExecutionPolicy.java

Purpose: This test suite verifies the security boundary in `ChatbotAgent` after the first LLM call has produced a candidate tool-call JSON but before any `ToolExecutor` network/API work is allowed. It protects against prompt injection causing disallowed Recon API access, path traversal, prefix confusion, absolute URL exfiltration, and partial execution of mixed valid/invalid multi-endpoint requests.

Important APIs/types/functions: The class uses mocked `LLMClient` and `ToolExecutor`, `OzoneConfiguration`, `ChatbotConfigKeys.OZONE_RECON_CHATBOT_ENABLED`, `OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE`, `OZONE_RECON_CHATBOT_MAX_TOOL_CALLS`, `ChatbotAgent.processQuery`, `LLMClient.LLMResponse`, and `ToolExecutor.ToolExecutionOutcome`. Mockito verification on `executeToolCallWithPolicy` is the central signal.

Control flow: `setUp` enables the chatbot and safe-scope enforcement, stubs the executor leniently, and constructs a `ChatbotAgent`. Each test configures the first LLM response as a raw JSON object. The agent parses that object, normalizes/validates endpoints, and either returns a direct rejection/fallback or proceeds to execution. These tests assert that disallowed endpoints never reach the executor and that most rejection paths require only one LLM call.

State and persistence behavior: There is no persistent state. Runtime state is limited to configuration-driven policy flags, parsed endpoint strings, parsed methods/parameters, and mocked invocation counts. The tests explicitly validate that blocked responses do not expose stack traces, internal package names, or chatbot credential config key fragments.

Dependencies and integration points: This suite anchors the integration between LLM output parsing, endpoint allowlist policy, path canonicalization, multi-tool batch validation, and the executor interface. It complements the parsing tests and endpoint tests by focusing on the Java-side policy layer that must remain authoritative even when the LLM emits malicious content.

Risks: Assertions mostly check non-execution and broad response text fragments, so they do not fully pin down exact user-facing rejection messages. The tests depend on the current allowlist semantics for `/api/v1/keys` boundary matching and canonical traversal handling. Multi-endpoint behavior is intentionally all-or-nothing; a future partial-execution policy would require deliberate test updates.

Test signals: Strong signals include `never()` calls to `executeToolCallWithPolicy` for `/api/v1/admin/delete`, external absolute URLs, `/api/v1/internal/secrets`, `/api/v1/keys2`, and traversal paths; `times(1)` LLM usage for direct rejection; and response-content checks for permitted-path wording without internal exception or config leakage.

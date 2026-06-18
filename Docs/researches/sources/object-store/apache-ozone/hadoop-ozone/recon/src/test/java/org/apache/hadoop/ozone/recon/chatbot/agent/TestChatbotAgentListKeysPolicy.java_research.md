# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentListKeysPolicy.java

Purpose: This class verifies `ChatbotAgent` handling for the sensitive `/api/v1/keys/listKeys` endpoint. It ensures safe-scope validation rejects broad key scans unless the LLM provides a bucket-scoped `startPrefix`, verifies disabling safe-scope allows root scans, checks parameter pass-through, and confirms executor/LLM failures are wrapped in `ChatbotException`.

Important APIs/types/functions: The suite uses `ChatbotAgent.processQuery`, mocked `LLMClient.chatCompletion`, mocked `ToolExecutor.executeToolCallWithPolicy`, `ChatbotException`, `OzoneConfiguration`, and `ChatbotConfigKeys.OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE`. `ArgumentCaptor<Map<String,String>>` validates exact executor parameters.

Control flow: `setUp` enables safe-scope and default executor success. Rejection tests return a `SINGLE_ENDPOINT` LLM JSON with absent, empty, root-only, or volume-only `startPrefix`; the agent must return a response without invoking the executor. Allowed tests return a bucket-scoped prefix and then a summary response, causing execution followed by a second LLM call. Exception tests inject `IOException` from the executor or runtime failure from the summarization call.

State and persistence behavior: There is no persistence. Runtime state includes the parsed parameters map, safe-scope boolean, max tool call count, and the two-stage LLM interaction. The disabled-safe-scope test constructs a second `ChatbotAgent` with a different config to prove policy is configuration controlled.

Dependencies and integration points: This suite binds LLM tool selection to Recon key-listing execution policy. It sits between general allowlist tests and `TestToolExecutorListKeys`, proving that the agent enforces bucket scoping before the executor handles pagination. It also validates that user/LLM filters such as `limit`, `replicationType`, and `keySize` survive routing.

Risks: The bucket-scope rule is tested syntactically as `/<volume>/<bucket>` and does not validate actual volume/bucket existence. Error wrapping assertions allow either execution or response-generation wording for summarization failure, which is resilient but less exact. Parameter values are strings, so type conversion is delegated elsewhere.

Test signals: No executor invocation for root/null/empty/volume-only prefixes; one executor invocation for `/vol1/bucket1`; execution allowed when `OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE=false`; preserved `IOException` cause and message; preserved summarization runtime cause; and captured optional parameters exactly matching the LLM JSON.

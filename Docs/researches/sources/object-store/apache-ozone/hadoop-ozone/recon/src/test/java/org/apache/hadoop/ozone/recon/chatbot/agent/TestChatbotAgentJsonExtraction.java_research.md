# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentJsonExtraction.java

Purpose: This compact suite tests `ChatbotUtils.extractFirstJsonObject`, the raw-text preprocessing step used to recover a JSON object from LLM output before Jackson/tool-call parsing. It verifies robustness against prose, markdown fences, nested objects, braces inside string values, escaped quotes, truncation, null/empty inputs, arrays, Unicode, control characters, and large string values.

Important APIs/types/functions: The only production API under test is `ChatbotUtils.extractFirstJsonObject(String)`. The tests use JUnit `assertEquals`, `assertNull`, `assertNotNull`, and `assertTrue` to verify exact extracted substrings or graceful null returns.

Control flow: Each test passes one raw string to the extractor. Happy paths expect the complete first balanced `{...}` object to be returned unchanged. Prose and markdown wrapper tests expect surrounding text/fences to be ignored. Invalid input tests expect `null`. Multiple-object and array tests document that extraction starts at the first `{` and returns the first balanced object only.

State and persistence behavior: There is no mutable shared state or persistence. The behavior under test is a local scanning algorithm that must maintain brace depth, string-mode state, and escape handling without parsing full JSON.

Dependencies and integration points: This utility feeds `ChatbotAgent` tool-call routing. Its output determines whether the agent enters `SINGLE_ENDPOINT`, `MULTI_ENDPOINT`, `DOCUMENTATION_QUERY`, or fallback flow. Returning a syntactically complete but semantically unknown object is intentional; later parsing/routing handles missing or unknown `type` fields.

Risks: The extractor is not a full JSON validator; it only finds a balanced object. Arrays produce the first inner object instead of rejecting the array. The large-json test checks no crash but does not enforce timing thresholds. Unicode/control-character cases protect scanner stability, not downstream JSON parser acceptance.

Test signals: Exact string equality for simple, nested, multi-endpoint, prose-wrapped, fenced, escaped-quote, and string-brace examples; `null` for truncated/no-object/sentinel/prose-only inputs; and non-null bounded-object shape for control-character and 10,000-character string cases.

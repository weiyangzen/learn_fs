# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestToolExecutorListKeys.java

Purpose: This suite verifies `ToolExecutor` handling of the paginated `listKeys` Recon API. It focuses on page aggregation, record/page counters, truncation when the configured page limit is reached, empty result handling, malformed prefix rejection, and propagation of HTTP/API `IOException`s.

Important APIs/types/functions: The tests use a spy of real `ToolExecutor`, `executeToolCallWithPolicy`, mocked `executeSingleCall`, `ToolExecutor.ToolExecutionOutcome`, Jackson `ObjectMapper`/`JsonNode`, and `ChatbotConfigKeys.OZONE_RECON_CHATBOT_EXEC_MAX_PAGES` plus `OZONE_RECON_CHATBOT_EXEC_PAGE_SIZE`.

Control flow: Setup constructs a real executor with max pages five and page size 200, then spies it so individual HTTP calls can be replaced with canned `JsonNode` pages. `testSinglePage` stops after a response without `lastKey`. `testMultiplePages` uses `lastKey` on page one to trigger a second call. `testMaxPagesLimit` returns an infinite page shape and expects termination at the caller-provided max. Error tests assert invalid `startPrefix` is rejected before any HTTP call and IO failures bubble up.

State and persistence behavior: There is no persistence. Runtime state includes the mutable request parameters passed between pages, aggregated `keys` array, records processed, pages fetched, and `truncated` marker in both the outcome and merged JSON body.

Dependencies and integration points: This class tests the execution engine used by the chatbot agent after safe-scope approval. It integrates Recon API response shape assumptions (`keys`, `lastKey`, `truncated`) with executor pagination policy and protects upper layers from unbounded listing.

Risks: Because `executeSingleCall` is mocked, URL construction and real HTTP behavior are not covered here. The tests do not inspect the `prevKey` or page parameter mutation, only call counts and merged output. Prefix validation duplicates some safe-scope intent at executor level and must stay aligned with the agent tests.

Test signals: Exact executor call counts of one, two, or three; `recordsProcessed`, `pagesFetched`, and `isTruncated` values; merged `keys` array lengths; `truncated=true` in capped output; `IllegalArgumentException` containing `requires 'startPrefix'` for missing/root prefix; and raw `IOException` message preservation for API failure.

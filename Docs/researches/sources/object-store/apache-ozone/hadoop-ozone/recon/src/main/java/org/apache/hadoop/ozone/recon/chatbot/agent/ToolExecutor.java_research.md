## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ToolExecutor.java

Purpose: singleton executor for chatbot tool calls against Recon REST APIs. It normalizes endpoints, builds loopback HTTP URLs from `ozone.recon.http-address`, applies connect/read timeouts from chatbot config, and returns a structured `ToolExecutionOutcome`.

Important APIs/types/functions: `executeToolCallWithPolicy` is the public entry point; `executeListKeysWithPaging` implements bounded pagination for `/keys/listKeys`; `executeSingleCall` performs GET/POST via `HttpURLConnection`; `buildUrl` substitutes path placeholders and URL-encodes query values; `ToolExecutionOutcome` carries response body, record/page counts, truncation, cursor, and applied limits.

Control flow: non-`listKeys` requests make one HTTP call and estimate record count. `listKeys` requires non-root `startPrefix`, caps page size by requested `limit` and policy, loops on `lastKey`, aggregates `keys`, and annotates the merged JSON with truncation metadata.

State and persistence: no durable state; state is request-local. Configuration is captured at construction. Integration points are `ChatbotAgent`, `ChatbotUtils`, Recon REST resources, `OzoneConfiguration`, and `ReconConfigKeys`.

Risks: plain `HttpURLConnection` does not send SPNEGO credentials, so Kerberos-protected Recon APIs return 401 as documented in the source. Placeholder path values are not encoded when inserted into the path, unlike query parameters. Pagination only special-cases one endpoint suffix. Tests should cover URL construction, listKeys cursor termination/truncation, error stream handling, null parameter maps, and Kerberos/error status behavior.

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/chatbot.types.ts

Purpose: Defines request/response and local message types for the v2 Assistant/chatbot feature.

Important APIs/types/functions: Exports `ChatbotHealthResponse`, `ChatbotModelsResponse`, `ChatbotChatRequest`, `ChatbotChatResponse`, `ChatbotErrorResponse`, and `ChatMessage`.

Control flow: Type-only contract. `ChatbotChatRequest` permits optional model/provider/userId, while `ChatMessage` models rendered conversation entries with role, text, timestamp, and optional model/provider.

State and persistence: No runtime state. `ChatMessage` is suitable for local UI state or persisted transcript storage elsewhere, but this file does not persist anything.

Dependencies and integration points: Used by v2 Assistant page and services integrating with chatbot health, model listing, and chat endpoints.

Risks: `ChatbotChatResponse` has only `response` and `success`; if failures return the separate `ChatbotErrorResponse`, callers must branch on HTTP/error handling rather than a discriminated union. `role` excludes future system/tool messages.

Test signals: API-client tests should cover health unavailable, empty model list, successful chat, error response, and optional model/provider propagation into rendered messages.

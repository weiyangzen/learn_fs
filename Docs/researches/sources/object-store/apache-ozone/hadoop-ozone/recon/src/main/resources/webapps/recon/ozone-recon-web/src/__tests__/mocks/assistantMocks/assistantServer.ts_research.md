# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/assistantMocks/assistantServer.ts


Purpose: MSW server and reusable handlers for Recon AI assistant tests.

Important APIs/types/functions: Exports health handlers (`mockHealthEnabled`, disabled, not configured), model handlers, chat handlers for success/delay/busy/timeout/error/disabled/interrupted/empty, and `assistantServer`.

Control flow/state/persistence: Handlers respond to `CHATBOT_ENDPOINTS.HEALTH`, `.MODELS`, and `.CHAT` with status-specific JSON. The default `assistantServer` includes enabled health, model list, and successful chat.

Dependencies/integration points: Used by `Assistant.test.tsx` and any future assistant tests. Model names encode provider choices consumed by the assistant UI.

Risks/test signals: Error bodies are user-facing contract fixtures. Model names can become stale as providers evolve. `mockModelsDisabled` and `mockChatEmpty` are available but not currently asserted by the visible tests.

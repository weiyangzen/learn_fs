# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/assistant/Assistant.test.tsx


Purpose: End-to-end component tests for the V2 Recon AI assistant page, covering health gating, model loading, chat success, provider-specific errors, disabled/busy/timeout states, and in-flight UI.

Important APIs/types/functions: `WrappedAssistantComponent`, `assistantServer`, multiple exported MSW handlers, `CHATBOT_ENDPOINTS`, `userEvent`, `waitFor`, and the real `Assistant` page.

Control flow/state/persistence: A single MSW server is opened for the suite. Each test installs handlers, renders inside `BrowserRouter`, waits for health-derived UI, interacts with input/provider dropdown/send/stop buttons, then clears `sessionStorage` and DOM in `afterEach`.

Dependencies/integration points: Integrates with `/api/v1/chatbot/health`, models, and chat endpoints via constants. It asserts markdown rendering, provider choices (`OpenAI`, `Google Gemini`, `Anthropic Claude`), and error message mapping.

Risks/test signals: The imported `rest` and `mockModelsDisabled` are unused. Tests reveal user-facing error contracts and state transitions; changes to labels/placeholders will break them.

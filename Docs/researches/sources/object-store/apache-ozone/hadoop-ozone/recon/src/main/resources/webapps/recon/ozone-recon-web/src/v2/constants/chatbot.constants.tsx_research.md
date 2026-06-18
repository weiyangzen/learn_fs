# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/chatbot.constants.tsx

Purpose: Centralizes Recon AI endpoints, provider/model classification, provider-specific error messages, loading-stage text, and seed prompts.

Important APIs, types, and functions: Exports `CHATBOT_ENDPOINTS`, `DEFAULT_MODEL_SENTINEL`, `PROVIDER_LABELS`, `getProviderForModel`, `resolveRequestProvider`, `isMaskedLlmProcessingError`, `getLlmProviderFailureMessage`, `LOADING_STAGES`, and `SEED_PROMPTS`.

Control flow: Model names are classified by lowercase prefixes. Error handling distinguishes generic/masked LLM failures from backend errors and returns provider-specific remediation text plus a server-log hint.

State and persistence behavior: Static constants and pure helpers only.

Dependencies: No imports.

Integration points: Used by Assistant, ModelPicker, LoadingIndicator, EmptyState, and `useChat`.

Risks and edge cases: Provider detection is prefix-based and misses newer model naming schemes unless updated. Error masking depends on backend exception text. Seed prompts are UI content coupled to backend query support.

Test signals: Cover model/provider classification, sentinel handling, masked error variants, provider failure message text, loading-stage thresholds, and seed prompt rendering.

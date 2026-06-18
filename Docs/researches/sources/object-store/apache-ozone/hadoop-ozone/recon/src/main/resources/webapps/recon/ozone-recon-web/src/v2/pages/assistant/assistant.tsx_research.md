# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/assistant.tsx

Purpose: Top-level Recon AI page coordinating feature health, model loading, chat state, disabled states, and composer/message layout.

Important APIs, types, and functions: Exports default `Assistant` React component.

Control flow: Fetches chatbot health on mount, fetches models only when health says enabled and LLM client available, gates rendering through loading/disabled/not-configured states, wires prompt chips to current query, and supports retry/regenerate by finding prior user messages.

State and persistence behavior: Local `isHealthLoaded` and `isModelsLoaded`; chat state and persistence come from `useChat`; API state comes from `useApiData`.

Dependencies: Uses AntD Spin/Button/Tag/icons, chatbot constants/types, `useApiData`, `useChat`, and assistant subcomponents.

Integration points: Loaded from v2 routes at `/Assistant` and linked by the nav/breadcrumb constants.

Risks and edge cases: The models effect depends on the whole `healthData.data` object, so identity changes can refetch. Retrying uses the latest user message and may not remove prior failed assistant/error state. Health errors show disabled/not-configured UI using default data.

Test signals: Cover health disabled, not configured, enabled with models load, model-load error, new chat disabled during in-flight, prompt click, retry, regenerate, and loading gate timing.

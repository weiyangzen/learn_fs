# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/DisabledState.tsx

Purpose: Displays the disabled or not-configured Recon AI page state.

Important APIs, types, and functions: Exports `DisabledState` with `reason: 'disabled' | 'not-configured'`.

Control flow: Branches on reason and renders an AntD `Result` warning with corresponding title/subtitle.

State and persistence behavior: Stateless.

Dependencies: Uses AntD `Result`.

Integration points: Used by Assistant after health check when chatbot is disabled or no LLM client is available.

Risks and edge cases: Messages are static and administrator-oriented. No action link or config docs are provided.

Test signals: Snapshot both reasons and verify warning status/title/subtitle.

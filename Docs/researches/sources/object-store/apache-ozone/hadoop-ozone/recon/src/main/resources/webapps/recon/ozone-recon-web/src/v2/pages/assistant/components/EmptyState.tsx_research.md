# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/EmptyState.tsx

Purpose: Initial Recon AI empty chat screen with hero text and seed prompt chips.

Important APIs, types, and functions: Exports `EmptyState` with `onPromptClick(prompt)`.

Control flow: Maps `SEED_PROMPTS` to clickable chips, maps prompt icon identifiers to AntD icons, and calls the parent with the selected prompt text.

State and persistence behavior: Stateless.

Dependencies: Uses chatbot constants, AntD icons, and `ReconAIMark`.

Integration points: Shown by Assistant when there are no persisted messages.

Risks and edge cases: Clickable chips are divs rather than semantic buttons, affecting keyboard accessibility. Prompt list depends on backend capabilities.

Test signals: Cover every seed prompt rendered, icon fallback, click callback payload, and accessibility/keyboard behavior if improved.

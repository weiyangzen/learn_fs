# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/LoadingIndicator.tsx

Purpose: Displays animated assistant loading state, stage text based on elapsed time, and long-request warning.

Important APIs, types, and functions: Exports `LoadingIndicator` with `elapsedSeconds` prop.

Control flow: Chooses the first `LOADING_STAGES` entry whose max seconds contains elapsed time, renders skeleton lines and typing dots, and shows a timeout warning after 60 seconds.

State and persistence behavior: Pure derived rendering; no local state.

Dependencies: Uses React `useMemo`, chatbot loading constants, and `ReconAIMark`.

Integration points: Used by `MessageList` while `useChat` has an in-flight request.

Risks and edge cases: The warning says timeout after 3 minutes but enforcement is backend/hook dependent. Stage thresholds must stay aligned with user expectations.

Test signals: Check stage boundaries at 3/10/45 seconds, long warning after 60 seconds, `aria-live` status, and active mark rendering.

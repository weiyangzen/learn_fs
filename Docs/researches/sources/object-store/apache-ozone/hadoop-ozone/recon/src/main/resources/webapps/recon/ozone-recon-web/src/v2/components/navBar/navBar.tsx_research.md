# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/navBar/navBar.tsx


Purpose: V2 sidebar navigation with feature-gated Heatmap and Recon AI links.

Important APIs/types/functions: `NavBar`, `NavBarProps`, `useApiData` calls for disabled features and chatbot health, and route menu items.

Control flow/state/persistence: Fetches `/api/v1/features/disabledFeatures` and chatbot health. Heatmap is shown when `HEATMAP` is not disabled; Assistant is shown when health loaded and enabled. Menu selected key tracks `useLocation().pathname`.

Dependencies/integration points: Used by new UI app shell. Integrates with `CHATBOT_ENDPOINTS.HEALTH`, logo asset, AntD `Sider/Menu`, and route paths.

Risks/test signals: Imports `useEffect` and stores `error` but does not use them. Chatbot link ignores `llmClientAvailable`, while the page itself handles not configured state. False menu items are spread among items.

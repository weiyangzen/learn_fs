# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorBoundary.tsx


Purpose: Generic React error boundary for V2 UI sections.

Important APIs/types/functions: `ErrorBoundary` class with props `fallback` and `children`, state `hasError`, `getDerivedStateFromError`, `componentDidCatch`, and `render`.

Control flow/state/persistence: Sets `hasError` when descendants throw during render/lifecycle, logs error info to console, and then renders fallback.

Dependencies/integration points: Can wrap fragile chart/table/page sections.

Risks/test signals: No reset behavior when children or route changes, so once tripped it stays tripped until remount. Fallback is generic and logging only goes to console.

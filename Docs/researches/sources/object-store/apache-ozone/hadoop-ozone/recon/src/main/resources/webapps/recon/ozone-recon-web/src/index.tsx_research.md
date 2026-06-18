# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/index.tsx


Purpose: Client entry point for the Recon React app.

Important APIs/types/functions: Imports React, `ReactDOM`, Roboto font weights, global `index.less`, and `App`; calls `ReactDOM.render(<App/>, document.querySelector('#root'))`.

Control flow/state/persistence: No local state. Bootstraps the app into the root DOM node.

Dependencies/integration points: Depends on the HTML root element and React 17-style render API.

Risks/test signals: React 18 migrations would replace `ReactDOM.render` with `createRoot`. If `#root` is absent, render receives null and fails at startup.

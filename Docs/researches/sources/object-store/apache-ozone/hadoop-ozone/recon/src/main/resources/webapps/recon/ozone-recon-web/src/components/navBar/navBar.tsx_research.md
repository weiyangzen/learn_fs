# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/navBar/navBar.tsx


Purpose: Legacy sidebar navigation for Ozone Recon.

Important APIs/types/functions: `INavBarProps`, `NavBar` class, `componentDidMount`, `fetchDisableFeatures`, and default `withRouter(NavBar)`.

Control flow/state/persistence: On mount, fetches `/api/v1/features/disabledFeatures` with axios, then enables/disables Heatmap based on whether `HEATMAP` appears. Renders fixed AntD `Sider` menu with route links and selected key from `location.pathname`.

Dependencies/integration points: Used by `app.tsx` old UI path; depends on logo asset, AntD Menu, route names, and `showDataFetchError`.

Risks/test signals: Props type includes state fields that are actually internal state. Heatmap is hidden on fetch failure. No direct tests in this subset cover legacy navbar.

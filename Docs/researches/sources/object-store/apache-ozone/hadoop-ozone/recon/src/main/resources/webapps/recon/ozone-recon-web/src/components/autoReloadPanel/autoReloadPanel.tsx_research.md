# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/autoReloadPanel/autoReloadPanel.tsx


Purpose: Legacy auto-refresh control panel that shows refresh time, OM DB sync time, manual refresh, auto-refresh toggle, and manual OM sync trigger.

Important APIs/types/functions: `IAutoReloadPanelProps`, `AutoReloadPanel` class, `autoReloadToggleHandler`, and default export wrapped in `withRouter`.

Control flow/state/persistence: Reads `sessionStorage.autoReloadEnabled` every render to set the switch default. Toggle delegates to parent `togglePolling`; reload and OM sync buttons call parent callbacks. Timestamps are formatted with Moment and exposed through tooltips.

Dependencies/integration points: Used by pages that own data polling via `AutoReloadHelper`; depends on AntD `Tooltip`, `Button`, `Switch`, and icons.

Risks/test signals: `Switch` uses `defaultChecked`, so it may not reflect external session changes after mount. `omStatus` is typed string but used truthily as status.

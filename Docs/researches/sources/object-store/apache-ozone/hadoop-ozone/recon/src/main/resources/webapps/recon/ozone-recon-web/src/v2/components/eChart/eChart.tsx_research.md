# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/eChart/eChart.tsx


Purpose: V2 ECharts wrapper with generic event handler support.

Important APIs/types/functions: Default `EChart`, `EChartProps` with `eventHandler`, ECharts `init`, `getInstanceByDom`, `setOption`, loading controls, and resize listener.

Control flow/state/persistence: Initializes/disposes chart on theme changes, registers `onClick` and arbitrary event handler, updates options/settings on dependency changes, and toggles chart loading.

Dependencies/integration points: Used by V2 overview, capacity, and insight plots. Tests often mock it because ECharts needs real layout.

Risks/test signals: Non-null assertions on chart instance can throw if initialization fails. Event handlers are registered on both init and update without removing old handlers, risking duplicates.

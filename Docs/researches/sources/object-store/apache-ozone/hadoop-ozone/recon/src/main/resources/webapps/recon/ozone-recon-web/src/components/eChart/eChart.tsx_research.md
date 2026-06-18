# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/eChart/eChart.tsx


Purpose: Legacy React wrapper around ECharts.

Important APIs/types/functions: Exports `EChartProps` and named function `EChart`. Props include `option`, `style`, `settings`, `loading`, `theme`, and `onClick`.

Control flow/state/persistence: Initializes chart on mount/theme change, registers click handler, adds window resize listener, disposes on cleanup, then updates options and loading state in separate effects.

Dependencies/integration points: Used by legacy charts and mocked in tests because jsdom cannot supply chart dimensions reliably.

Risks/test signals: `getInstanceByDom` can return undefined, but code calls `chart.setOption`/`showLoading` without null checks. Re-registering click handlers on option updates may duplicate handlers.

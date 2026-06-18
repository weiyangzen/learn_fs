# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/overviewCard/overviewCard.tsx


Purpose: Legacy Overview metric card with icon selection, optional storage bar, error highlighting, and optional link wrapping.

Important APIs/types/functions: `IconSelector`, `OverviewCardWrapper`, `OverviewCard`, `IOverviewCardProps`, and storage integration via `IStorageReport`.

Control flow/state/persistence: Selects icon by string, marks card error when `error` or `data === 'N/A'`, embeds `StorageBar` when `storageReport` exists, and wraps cards in `Link`. For `/Om`, it derives tab state from card title.

Dependencies/integration points: Used by legacy Overview and OM Insights navigation.

Risks/test signals: `OverviewCardWrapper` reaches into `children._owner.stateNode.props`, a React internal that is brittle and unsafe. V2 wrapper replaces this with explicit title props.

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewCardWrapper.tsx


Purpose: V2 link wrapper for overview cards, including OM Insights tab routing.

Important APIs/types/functions: Default export `OverviewCardWrapper`, `OverviewCardWrapperProps`, local `setCurrentActiveTab`.

Control flow/state/persistence: If `linkToUrl === '/Om'`, wraps children in `Link` with `state.activeTab` derived from title. Otherwise wraps in a normal `Link` when `linkToUrl` is non-empty, or returns children unchanged.

Dependencies/integration points: Used by V2 overview cards that navigate to detail pages and OM tabs.

Risks/test signals: Title string matching (`Open Keys Summary`, `Pending Deleted Keys Summary`, `OM Service`) is fragile; renaming cards changes navigation state.

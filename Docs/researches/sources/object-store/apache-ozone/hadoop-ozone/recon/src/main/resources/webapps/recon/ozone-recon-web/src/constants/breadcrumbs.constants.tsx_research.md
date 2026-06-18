# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/breadcrumbs.constants.tsx


Purpose: Legacy route-to-label map for breadcrumbs.

Important APIs/types/functions: Exports `breadcrumbNameMap` with labels for Overview, Volumes, Buckets, Datanodes, Pipelines, Missing Containers, Containers, Insights, Namespace Usage, Heatmap, and Om.

Control flow/state/persistence: None; constants only.

Dependencies/integration points: Consumed by legacy `Breadcrumbs`. Must align with `routes.tsx` and nav menu paths.

Risks/test signals: Missing `/Capacity` and `/Assistant` reflect legacy route scope. Unknown route breadcrumbs render undefined labels.

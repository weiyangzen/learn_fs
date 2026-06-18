# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/rightDrawer/rightDrawer.tsx


Purpose: Legacy right-side metadata summary drawer.

Important APIs/types/functions: Exports `DetailPanel` class. Props include `visible`, `keys`, `values`, and `path`.

Control flow/state/persistence: Mirrors incoming `visible` to local state using `componentWillReceiveProps`, closes locally, zips `keys` and `values` into table rows, and renders AntD Drawer/Table.

Dependencies/integration points: Used by legacy namespace/disk usage metadata views.

Risks/test signals: References `RouteComponentProps` without import. `keys`/`values` are typed as empty tuple arrays (`[]`), losing real element types. Close state is internal only, so parent visibility may become inconsistent.

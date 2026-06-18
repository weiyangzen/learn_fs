# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorCard.tsx


Purpose: Visual error placeholder card for V2 overview/summary cards.

Important APIs/types/functions: Default `ErrorCard`, props `title` and optional `compact`, uses `DisconnectOutlined` and AntD `Card`.

Control flow/state/persistence: Stateless. Chooses compact or large body padding and emits `data-testid="error-${title}"`.

Dependencies/integration points: Used by V2 overview cards, health cards, and storage cards when data is missing/error.

Risks/test signals: If `title` is a React node, test id becomes unhelpful (`[object Object]`). The card displays only an icon, so accessibility text may be limited.

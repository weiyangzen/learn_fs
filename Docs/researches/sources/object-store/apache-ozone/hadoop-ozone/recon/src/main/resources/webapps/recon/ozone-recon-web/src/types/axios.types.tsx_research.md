# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/axios.types.tsx


Purpose: Minimal axios response typing helper.

Important APIs/types/functions: Exports generic `IAxiosResponse<T>` with `data: T`.

Control flow/state/persistence: None.

Dependencies/integration points: Intended for components/helpers that want a narrowed response type without importing full axios generics.

Risks/test signals: It only models `data`, omitting status/headers/config. Overuse can hide response metadata needs.

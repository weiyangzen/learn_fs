# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/quotaBar/quotaBar.tsx


Purpose: Legacy quota usage progress bar with tooltip metadata.

Important APIs/types/functions: `IQuotaBarProps`, `QuotaBar` class, `renderQuota` helper, and default `withRouter`.

Control flow/state/persistence: Computes `remaining = quota - used`, formats size quotas with `filesize`, and renders AntD `Progress` using `getCapacityPercent(used, quota)`. Tooltip shows used and remaining with themed square icons.

Dependencies/integration points: Used by legacy volume/bucket namespace quota displays. Depends on `FilledIcon`, `getCapacityPercent`, AntD `Progress`, and `filesize`.

Risks/test signals: Quota `<= -1` displays `-`, but percent still divides by quota, producing negative/invalid percentages. No direct tests cover this component.

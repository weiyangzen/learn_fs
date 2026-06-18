# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres.go

Purpose: defines time-bucket resolution functions used by metrics time-series aggregation.

Important APIs/types/functions: `TimeResolutionFunc`, `TimeResolutionByHour`, `TimeResolutionByDay`, `TimeResolutionByQuarter`, `TimeResolutionByWeekStartingSunday`, `TimeResolutionByWeekStartingMonday`, `TimeResolutionByMonth`, `TimeResolutionByYear`, `startOfSundayBasedWeek`, `startOfMondayBasedWeek`, and `startOfQuarter`.

Control flow: each resolution function returns the start of the containing period and the start of the next period in the timestamp's location. Hour uses `Truncate(time.Hour)`; day/month/year use calendar construction; week helpers subtract weekday offsets; quarter rounds month to the first month of its quarter.

State/persistence behavior: no state is stored. Returned boundaries determine how historical snapshots are bucketed and therefore affect time-series output.

Dependencies/integration: consumed by `CreateTimeSeries` and tests. Uses `time.Location` from the input timestamp, so local-time snapshots retain local calendar boundaries.

Risks/test signals: `TimeResolutionByWeekStartingMonday` comment says Sunday even though implementation starts Monday. DST transitions can make calendar periods non-24-hour; this is likely desired for local calendar aggregation but important for proportional ratios.

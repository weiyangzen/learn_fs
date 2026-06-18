## sources/test-tools/syzkaller/syz-cluster/series-tracker/main_test.go

`TestSeriesProcessor` verifies that `seriesProcessor.Process` extracts message bodies and accumulates email addresses from parsed messages. The expected address set includes From, To, and Cc addresses as returned by syzkaller's email parser, sorted by `Emails`.

The test covers the local processing helper used before `UploadSeries`. It does not cover lore polling, corrupted series handling, duplicate series, or session upload failures.

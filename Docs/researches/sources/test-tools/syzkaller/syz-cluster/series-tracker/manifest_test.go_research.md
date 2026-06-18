## sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest_test.go

`TestParseManifest` validates manifest parsing with two inboxes and multiple epochs. It asserts map length, epoch count for the first inbox, epoch count for the second, and URL construction for epoch 1.

The test is a focused signal for key parsing and max-epoch aggregation. It does not cover malformed keys beyond log-only behavior, gzip download, HTTP errors, or `ManifestSource` concurrency/blocking.

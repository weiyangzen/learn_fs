# sources/user-network-fs/rclone/lib/transform/transform.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform.go -->
## sources/user-network-fs/rclone/lib/transform/transform.go

Purpose: applies configured path/name transformations for rclone's `convmv` and name-transform support. It includes Unicode normalization, base64, prefix/suffix/trim/truncate, encoder/decoder, charmap, case, ASCII, URL, date, regex, and external command transforms.

Important APIs and control flow: `Help()` returns embedded generated help with the banner removed. `Path(ctx, s, isDir)` loads parsed options, skips file-only transforms for directories, applies directory-only transforms to parent paths for files, logs/counts no-retry errors, and refuses transforms that change the number of path separators. `transformPath` applies a transform to each path segment or only the base. `transformPathSegment` switches on `Algo` and performs the actual conversion. Helpers handle extension preservation, rune/byte truncation without splitting UTF-8, segment validation, time glob parsing, and external command invocation.

State, dependencies, and integration: depends on embedded `transform.md`, rclone `fs`, `fserrors`, `encoder`, `x/text` normalization/charmaps, `exec`, `regexp`, `url`, and time. It integrates with config via `options.go` and logs transformed paths through rclone logging.

Risks and test signals: `transformPath` preallocates `transformedSegments := make([]string, len(segments))` and then appends, which can insert leading empty segments before `path.Join`; tests may miss some all-segment paths. `regexp.MustCompile` can panic on invalid regex values. `command` executes an external binary with the path as an argument, a deliberate but high-risk feature. Validation prevents empty or slash-containing segments and reverts if separator count changes. Tests cover tag selection and representative transforms, but not every transform or error path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform.go -->

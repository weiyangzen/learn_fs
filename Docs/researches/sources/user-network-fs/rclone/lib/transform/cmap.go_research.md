# sources/user-network-fs/rclone/lib/transform/cmap.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/cmap.go -->
## sources/user-network-fs/rclone/lib/transform/cmap.go

Purpose: exposes selectable character maps and helpers for lossy character-map transformations in the name-transform feature.

Important APIs and control flow: `CharmapChoices` is an `fs.Enum`. `cmapChoices.Choices()` iterates `charmap.All`, keeps `*charmap.Charmap` entries, creates display names by replacing spaces with hyphens, records each charmap in the package `cmaps` map under its enum index, and returns the choices. `charmapByID` looks up a charmap by enum value. `encodeWithReplacement` maps each rune through the charmap, replacing unencodable runes with `_`. `toASCII` strips non-ASCII runes.

State, dependencies, and integration: global `cmaps` is protected by `lock`. This file depends on `fmt`, `strings`, `sync`, rclone `fs`, and `x/text/encoding/charmap`. It integrates with `transformPathSegment` for `ConvCharmap`, legacy ISO-8859-1, Windows-1252, Macintosh, and ASCII transforms.

Risks and test signals: `charmapByID` relies on `Choices()` having populated `cmaps`; enum parsing normally calls `Choices`, but direct use before choices could return nil. Tests in `transform_test.go` cover some charmap output through high-level path transforms, not this map population directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/cmap.go -->

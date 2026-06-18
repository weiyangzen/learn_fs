## sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer_test.go

Purpose: Tests ASCII I/O renderer formatting and validation.

Important APIs/types/functions: tests for `NewRenderer`, `NewRendererWithSettings`, `humanReadable`, `mapCoord`, `Render`, golden output comparisons, and invalid range handling.

Control flow: constructor tests check invalid and valid settings; mapping tests cover start/end/middle offsets; render tests compare exact strings from testdata golden files for default/custom settings and different file sizes.

State and persistence behavior: reads golden files under `testdata/io_renderer`; no writes unless commented regeneration lines are enabled.

Dependencies and integration points: validates user-visible debugging output exactly, including whitespace and block characters.

Risks: golden files make output changes intentional but can be brittle for formatting tweaks. Invalid settings test labels mention zero label width but use valid label widths in valid cases.

Test signals: strong regression signal for chart layout and range validation.

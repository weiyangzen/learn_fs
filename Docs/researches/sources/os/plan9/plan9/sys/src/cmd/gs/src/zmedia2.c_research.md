# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmedia2.c

LanguageLevel 2 media matching support for `setpagedevice`. It implements `.matchmedia` and `.matchpagesize`, matching requested page/device attributes against an `InputAttributes`-style dictionary and policy dictionary.

`.matchmedia` validates request, attributes, policies, and key array; handles null attribute dictionaries; extracts requested `MediaPosition`, `Orientation`, and `RollFedMedia`; applies `PolicyNotFound`; and scans candidate media dictionaries. Non-`PageSize` keys require object equality. `PageSize` uses `zmatch_page_size`, which supports exact/ranged media arrays, orientation, roll media, and policy-based nearest/next-larger matching.

`match_page_size` uses a tolerance of 5 units, computes mismatch penalties, prefers better size fits and priority ordering, and can generate an adjustment matrix for scaling/rotation. `make_adjustment_matrix` centers, rotates, optionally scales, and translates the page according to the selected medium. The code notes a limitation for variable-size media when the match is not exact.

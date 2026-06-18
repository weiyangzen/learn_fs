# sources/object-store/minio-mc/cmd/duration.go

Purpose: Extends Go duration parsing with days, weeks, and years for mc time filters.

Important APIs/types/functions: `Duration`, `Days`, unit constants, `leadingInt`, `unitMap`, and `ParseDuration`.

Control flow: `ParseDuration` mirrors Go's duration parser: optional sign, repeated numeric/fractional unit chunks, overflow checks, unit lookup, fractional scaling, and final sign application. It rejects empty, missing-unit, unknown-unit, and overflow inputs.

State and persistence: Stateless.

Dependencies/integration: Used by age/rewind-related helpers elsewhere for flags such as `--older-than`, `--newer-than`, and retention duration parsing.

Risks: Month/year-related constants are approximations, though only `y` appears in `unitMap`. `Duration.Days` appears to return hours plus fractional days due to dividing the remainder by day but not the main hour count by 24, which may be unintended.

Test signals: No direct tests in this subset.

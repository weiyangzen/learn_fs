<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/i18n/en.toml -->
# sources/user-network-fs/rclone/docs/i18n/en.toml

## Purpose

`en.toml` is a minimal Hugo i18n file used to quiet monolingual-site translation warnings.

## Important APIs, Types, and Functions

It defines the `[wordCount]` translation with `other = "{{ .WordCount }} words"`.

## Control Flow

Hugo loads the file during site generation when templates request localized word-count text.

## State and Persistence Behavior

No runtime or persistent state is created beyond generated site text.

## Dependencies and Integration Points

It integrates with Hugo's i18n subsystem and any template using `i18n "wordCount"`.

## Risks and Test Signals

Risks are low: syntax errors can break docs builds, and missing keys may reintroduce warnings. A Hugo build is the main test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/i18n/en.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/config.json -->
# sources/user-network-fs/rclone/docs/config.json

## Purpose

`docs/config.json` is the Hugo site configuration for rclone.org documentation.

## Important APIs, Types, and Functions

It defines taxonomy index names, base URL, title/description, ignored files, Git info, disabled taxonomy kind, table-of-contents bounds, Goldmark parser/renderer settings, and syntax-highlighting class output.

## Control Flow

Hugo reads this config during docs builds, applies ignored-file filters, renders markdown with configured heading IDs and unsafe HTML disabled, and builds menus/tags/groups from indexes.

## State and Persistence Behavior

No runtime state is stored. Build output depends on this config and source content.

## Dependencies and Integration Points

It integrates with Hugo, Goldmark, rclone docs layouts, data files, and generated command/backend pages.

## Risks and Test Signals

Risks include broken anchors from heading-ID changes, missing taxonomy output expected by templates, unsafe HTML behavior changes, and base URL drift. Tests should run the Hugo build and check generated links, TOC, and backend data pages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/config.json -->

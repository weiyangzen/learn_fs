# sources/security-integrity/cryfs/crates/check/src/error/display/error_title.rs

Purpose: This module centralizes the title line used by corruption error displays.

Important APIs and flow: `ErrorTitle` stores static `error_type` and `error_message`. Its `Display` implementation renders `Error[type]: message` with colored/bold styling through `console::style`.

State and persistence: It is a small value object with no runtime state beyond static strings.

Dependencies and integration: It is used by blob and node display helpers and by every concrete error's `Display` implementation through a local constant.

Risks and test signals: Because all display tests include this first line, changes to wording or ANSI style can ripple across snapshots. Styling is isolated, making text semantics easy to preserve.

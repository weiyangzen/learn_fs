<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gendocs/gendocs.go -->
# sources/user-network-fs/rclone/cmd/gendocs/gendocs.go

## Purpose

`gendocs.go` implements `rclone gendocs`, generating Hugo-compatible Markdown command documentation and a global flags page from the Cobra command tree.

## Important APIs, Types, and Functions

`frontmatter` and `frontmatterTemplate` define generated page metadata. The command creates the output tree, executes `help flags` into `flags.md`, builds command alias/annotation metadata recursively, customizes Cobra doc generation with a prepender and link handler, then walks generated files to replace inherited-option sections with grouped flag help and normalize headings.

## Control Flow

Generation proceeds in phases: create dirs, render flags, collect command details, run `doc.GenMarkdownTreeCustom`, then munge each generated command page. Certain mount docs are skipped on platforms where commands are unavailable.

## State and Persistence Behavior

It writes and rewrites many local Markdown files under the requested output directory and toggles `cmd.GeneratingDocs`.

## Dependencies and Integration Points

It integrates with Cobra docs, root command metadata, rclone flag groups, `lib/file.MkdirAll`, runtime GOOS checks, templates, regexes, and generated website frontmatter conventions.

## Risks and Test Signals

Risks include command/detail map mismatches, brittle string cut points, platform-specific skipped docs, annotation/frontmatter escaping, global command args/output mutation, and broad file rewrites. Tests should generate docs into temp dirs, verify frontmatter, flags page, aliases, group help insertion, skipped platform docs, and idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gendocs/gendocs.go -->

# sources/sync-backup/kopia/site/hugo.toml

Purpose: configures the Kopia documentation website built with Hugo and the Docsy theme.

Important APIs/types/functions: sets `baseURL`, title, robots, git info, content/static directories, language settings, disabled taxonomy kinds, Chroma/Pygments highlighting, top menu entries, blog permalinks, BlackFriday options, image processing, UI params, feedback text, footer links, and Hugo module imports for `github.com/google/docsy` and dependencies.

Control flow: Hugo reads this declarative config during build/server. Menu and module sections drive navigation and theme resolution. `services.googleAnalytics` is intentionally empty because analytics are handled manually, while feedback config is enabled but depends on analytics ID to function.

State and persistence behavior: no runtime state. The config controls generated URLs, rendered navigation, theme modules, and image processing output.

Dependencies/integration: integrates with Hugo extended version at least 0.73.0, Docsy modules, Git metadata, site content under `content`, static files under `static`, and GitHub edit links pointing at the `site` subdirectory on `master`.

Risks: `enableGitInfo` depends on Git availability in build environments. BlackFriday settings are legacy relative to modern Hugo/Goldmark defaults. Module proxy is set to `direct`, which can affect reproducibility/network behavior.

Test signals: validated by Hugo build; no automated test in this file.

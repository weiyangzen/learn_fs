# sources/object-store/apache-ozone/hadoop-hdds/docs/config.yaml

## Purpose
This is the Hugo site configuration for the Apache Ozone HDDS documentation module. It sets site language metadata, title, theme, URL behavior, Markdown rendering, and security allowances for selected environment variables.

## Important configuration
- `languageCode: en-us`, `DefaultContentLanguage: en`.
- Two languages are declared: English with weight 1 and Chinese with weight 2.
- Site title is `Ozone`.
- `params.ghrepo` points at `https://github.com/apache/ozone/`.
- Theme is `ozonedoc`.
- `pygmentsCodeFences: true` enables code highlighting for fenced blocks.
- `uglyurls: true` and `relativeURLs: true` control generated URLs for static packaging.
- Taxonomy and taxonomyTerm page kinds are disabled.
- Goldmark `renderer.unsafe: true` allows raw HTML in Markdown.
- Hugo security allows `getenv` for variables matching `^HUGO_` and `^OZONE_VERSION$`.

## Control flow
Hugo reads this file at site generation time. The settings determine content language selection, theme loading, output URL construction, Markdown rendering, and which environment variables templates may access. The `OZONE_VERSION` allowance is paired with the generation script that exports the Maven-derived project version.

## State and persistence
No mutable application state is stored here. The persistent output effect is the generated static documentation tree, especially links and HTML rendering behavior under the build target.

## Dependencies and integration points
This integrates with Hugo, the local `ozonedoc` theme under `docs/themes`, Markdown content, theme templates that may call `getenv`, and `docs/dev-support/bin/generate-site.sh` which exports `OZONE_VERSION`.

## Risks and edge cases
- `unsafe: true` permits raw HTML from docs content; this is common for documentation sites but increases review burden for untrusted content.
- `relativeURLs` and `uglyurls` are important for packaged docs. Changing either can break links in the built jar or static artifact.
- Only `HUGO_*` and `OZONE_VERSION` environment variables are allowed to templates; adding template usage of other environment variables will fail under Hugo security.
- The `DefaultContentLanguage` key uses Hugo's historical capitalization; config parser behavior should be checked when upgrading Hugo.

## Test signals
Run the docs generation path and inspect generated links, language output, syntax-highlighted code blocks, raw HTML rendering, and any template version display using `OZONE_VERSION`. A Hugo config validation/build with the repo's supported Hugo version is the best signal.

# sources/sync-backup/kopia/site/static/favicons/browserconfig.xml

Purpose: provides Microsoft browser tile metadata for Kopia favicons.

Important APIs/types/functions: XML root `browserconfig` contains `msapplication/tile`, a `square150x150logo` pointing to `/favicons/mstile-150x150.png`, and tile color `#da532c`.

Control flow: browsers that support this metadata fetch it from the static site and use it for pinned tiles.

State and persistence behavior: static asset configuration only. It is copied into Hugo output with other static files.

Dependencies/integration: depends on the referenced PNG existing under static favicons and on the site serving `/favicons/...` paths.

Risks: missing or renamed favicon assets break tile rendering. Color changes affect platform branding.

Test signals: validated by static site build/output inspection or browser favicon checks; no code tests.

# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/www/stats.js

`stats.js` drives the Venti web statistics dashboard. It defines graph query names, labels, column layouts, logging/stat/compression controls, and log links, then dynamically builds graph tables using `/graph?...` image URLs.

Clicking a small graph promotes it to the two large 24-hour and 1-hour graphs. The settings panel updates local state and sends changes through a hidden frame URL `/set/<name>/<value>`.

The script is old-style global JavaScript/DOM code and depends on server endpoints for graph images, logs, and settings. It includes HTML snippets directly in strings.

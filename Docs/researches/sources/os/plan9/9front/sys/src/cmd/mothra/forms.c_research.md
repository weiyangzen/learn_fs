# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/forms.c

Implements Mothra HTML form parsing, widget construction, form interaction, encoding, submission, and cleanup.

Key behavior:
- Defines `Form`, `Field`, and `Option` structures for HTML forms and controls.
- `rdform()` handles `form`, `input`, `button`, `select`, `option`, `textarea`, and `isindex` tags, creating fields and output placeholders.
- `mkfieldpanel()` converts parsed fields into libpanel widgets: entries, password entries, check/radio buttons, submit/reset buttons, file picker buttons, select pulldowns, text windows, and index fields.
- Handles checkbox/radio/select state changes, reset behavior, file upload path prompting, and Enter-to-submit behavior for single text fields.
- Encodes submissions as URL-encoded GET/POST or multipart form-data with a fixed boundary.
- `h_submitinput()` dispatches GET via a generated URL and POST via `urlpost()`/`geturl()`.
- `freeform()` releases forms, fields, options, and panels.

Important dependencies: Mothra browser types/functions, `html.h`, `rtext.h`, libpanel widgets, `geturl`, `urlpost`, `filetype`, global display state.

Notable risks:
- Multipart boundary is a fixed constant.
- Form controls directly own panels and interact with global `screen`, `text`, `mouse`, `font`, and `chrwidth`.
- File inputs deliberately clear HTML-provided default paths.

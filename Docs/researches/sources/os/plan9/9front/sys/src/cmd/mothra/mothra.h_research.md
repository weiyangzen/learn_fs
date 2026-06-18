# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.h

Shared Mothra declarations and constants.

Defines:
- Browser limits: page history size, parallel image loader count, image memory budget, name/line/auth/title/label lengths, and redirect limit.
- Core structures:
  - `Action`: link/image/form/name metadata attached to rendered `Rtext`.
  - `Url`: relative/base/full URL state, fragment tag, content type, and image-map flag.
  - `Www`: one cached page, including URL, image/form storage, title, rendered text, scroll offset, and async status flags.
  - `Field`: forward declaration for form support.
- File/content type enum values for plain text, HTML, common image formats, icons, and page-rendered document types.
- Authentication and HTTP method constants.
- Shared globals for drawing assets, character width, current text panel, debug flag, and mouse state.
- Function prototypes across Mothra modules: parsing/rendering, URL resolution/fetch/post, image handling, form cleanup, MIME detection, panel creation, message reporting, and formatting.

This header is the local contract between Mothra’s UI, HTML reader, URL backend, MIME snooper, image loader, and form code.

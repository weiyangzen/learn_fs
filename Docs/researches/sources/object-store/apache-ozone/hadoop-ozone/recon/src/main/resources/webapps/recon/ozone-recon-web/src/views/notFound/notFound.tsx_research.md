# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/notFound/notFound.tsx

Purpose: Minimal legacy 404 component.

Important APIs/types/functions: Exports `NotFound: React.FC`, rendering a `page-header` with `404 Page Not Found :(`.

Control flow: No branching or interaction; it only renders static markup.

State and persistence: Stateless and side-effect free.

Dependencies and integration points: Used by the legacy route layer or app shell as a fallback page. Depends only on React and existing CSS for `page-header`.

Risks: No navigation action, explanatory text, or route recovery option is provided. The legacy and v2 404 pages have different UX and export styles.

Test signals: Simple render test should assert the 404 message is visible.

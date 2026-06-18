# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/notFound/notFound.tsx

Purpose: v2 404 page with an inline SVG illustration and a primary "Go Back" button.

Important APIs/types/functions: Defines `notFoundIcon`, `contentStyles`, and functional component `NotFound`. It uses Ant Design `Button`, `ArrowLeftOutlined`, and React Router `useHistory`.

Control flow: Rendering centers the SVG, message text, and button. Clicking the button calls `history.goBack()`, delegating navigation behavior to React Router browser history.

State and persistence: Stateless component with no side effects beyond history navigation. The SVG is embedded directly in the module, so no asset loading or caching dependency is required.

Dependencies and integration points: Used as the fallback page in the v2 route layer or app shell. It depends on Ant Design styling and React Router history context.

Risks: `goBack()` may keep users on an invalid route if the previous entry is also invalid or if there is no meaningful prior page. The inline SVG is large and includes fixed font references, which can affect bundle size and rendering consistency.

Test signals: Tests should verify that the component renders a 404 message and that clicking the button invokes `history.goBack`.

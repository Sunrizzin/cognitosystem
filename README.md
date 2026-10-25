# Cognito System landing page

Static website for [cognitosystem.com](https://cognitosystem.com/).

## Structure

- `index.html` — product landing page
- `gcse-revision.html`, `a-level-revision.html` — exam-board guides built from the app's specification catalog
- `exam-study-plan.html` — study-plan guide
- `media/` — looping screen recordings of the app and their posters, built by `tools/make_media.py` from the app repository's captures
- `privacy.html` — Privacy Policy
- `terms.html` — Terms of Use
- `sitemap.xml` and `robots.txt` — search discovery
- `llms.txt` — concise product facts for AI systems

The site intentionally uses no external JavaScript, analytics, ad trackers, web fonts, or build step. The home page carries one small inline script that plays the recordings and runs the sample review; everything it touches stays readable without it. Open `index.html` directly or serve this directory with any static HTTP server.

## Publishing checklist

1. Review product claims against the current App Store release.
2. Review Privacy Policy and Terms whenever data flows, providers, subscriptions, or legal requirements change.
3. Confirm all internal links and the App Store URL.
4. Update `sitemap.xml` dates.
5. Test desktop, mobile, keyboard navigation, and reduced-motion behavior.

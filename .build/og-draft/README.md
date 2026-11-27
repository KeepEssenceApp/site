# Share image: a DRAFT, not a site asset

`og-1200x630-DRAFT.png` is the candidate share image from Marketing (marketing repo, commit `3fa16d5`,
`content/site-refresh-2026-11-27/`, with `make_og_draft.py`, which stays there: it draws from that repo's
`brand/build.py`). Light page palette and the headline "存得下很多，只留精华。 / Save a lot. Keep only the essence."

**It is not approved.** The headline is taken from site PR #3 and has not been finally approved by Cheney.
Until it is:

- it is not in `assets/`, no page names it, and `.build` is in `.assetsignore`, so it is not published;
  `python3 .build/check.py` fails if a file with DRAFT in its name is served or a page names one;
- the pages still name `assets/keepessence-og-1200x630.png`, which is the **old** image, with the old tagline
  "阅尽千芳，只留精华" in the picture (sha256 `44b75cca…`). It must not go out with the new copy:
  `python3 .build/check.py --release` fails while that file is the old one, and the plain run prints a note.

To publish: take the approved image from Marketing (not this file, unless it is the approved one), put it at
`assets/keepessence-og-1200x630.png`, run `python3 .build/check.py --release`, and delete this folder.

# news-image-20261120 — notes

This entry is a pure-stdlib Python program (`main.py`) that draws a
1024x1024 front-page image summing up Friday 20 November 2026.
The page follows the previous days' shape: one wide lead story on
top, four stories in a 2x2 grid, and a single strip along the bottom.

## The six stories (researched 2026-11-20 ~08:00 WIB, from that day's reporting)

1. CHINA - SUMMIT (lead): Trump, Xi and Putin sign a four-point
   "peace declaration" after their first-ever trilateral summit in
   Shenzhen: a nuclear war cannot be won and must never be fought,
   but no arms-control talks, no timetable, and no mention of
   Ukraine or Iran. Trump holds a press conference in Washington
   at noon on Friday.
2. GULF - IRAN: Trump pushes the Iran war decision to 2027: no rush,
   he will "see what happens" after January 1.
3. WORLD COURT: The International Court of Justice rules Myanmar
   committed genocide against the Rohingya minority.
4. SPACE - NASA: NASA confirms Voyager 1 is now a full light-day
   from Earth — 24 hours for a radio signal to reach the probe.
5. WEATHER - INDIA: Cyclone Akvan bears down on Odisha: 300,000
   evacuated, 423 rescue teams deployed.
6. CULTURE - GAMES: Grand Theft Auto VI sales pass The Odyssey's
   $1.80 billion global run.

## Local verification (2026-11-20 ~08:10 WIB)

- `python3 -m py_compile main.py`: OK.
- Two runs into different output dirs: byte-identical entry.png,
  sha256 4b383dbfd37cea802884232872cb2d69062ede33617df5df400fc8afb76c5ecb.
- PNG valid (signature + IHDR 1024x1024), 40,715 bytes (cap 1,048,576).
- Rendered image inspected visually: masthead date legible, all six
  headlines + subheads legible, scenes read (three flags + dove over
  the Shenzhen skyline, 2027 calendar + clock, scales of justice,
  Voyager probe + signal rings, cyclone spiral + waves, Vice City
  sunset + VI).
- Fixes during the build: lead and ICJ subheads shortened to fit
  their line caps; Voyager signal rings drawn before the probe so the
  craft sits on top; cyclone waves moved to the very bottom and the
  300,000/EVACUATED callout moved up (scale-2 text is 14px tall, not
  7px — the waves had crossed the gold text); ICJ label moved inside
  its 48px band; GTA palms moved to the scene edges, clear of the VI.

## Repo

- jekglory/news-image-20261120, PUBLIC, MIT (SPDX line), created
  after the 2026-11-20T00:00:00Z opening.
- Files: main.py, LICENSE, README.md, NOTES.md, .makefun/owner.json.

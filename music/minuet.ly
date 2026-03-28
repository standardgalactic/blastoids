\version "2.24.1"

\header {
  title = "Minuet Sketch"
  subtitle = "approximate reconstruction from remembered melody"
  composer = "unknown"
  tagline = ##f
}

global = {
  \key g \major
  \time 3/4
  \tempo "Moderato" 4 = 108
}

melody = \relative c'' {
  \global

  r4 g4 |
  b4 d4 b4 |
  b2 d16 e fis g |
  a8 b c d e8 d8 |
  c4 a4 fis4 |
  g2 e8 g8 |
  a8 b g8 e8 g4 |
  a8 g8 e4 fis8 g8 |

  b8 g8 cis8 c8 a8 fis8 |
  d4 b4 g4 |
  b4 d4 b4 |
  a2 a8 b8 |
  d8 a'8 d,4 b4 |
  d4 a'4 d,4 |
  d4 a8 b8 c8 d8 |
  d4 a'4 d,4 |

  d4 a'4 d,4 |
  b4 a'4 d,4 |
  d4 a'4 g8 fis8 |
  e4 g,4 b8 c8 |
  d4 b4 g4 |
  b4 d4 a'4 |
  g,8 b8 d8 e8 g8 a8 |
  b2. \bar "|."
}

\score {
  \new Staff \with {
    midiInstrument = "acoustic grand"
  } {
    \clef treble
    \melody
  }
  \layout { }
  \midi { }
}

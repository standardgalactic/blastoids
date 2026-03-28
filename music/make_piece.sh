#!/usr/bin/env bash

cat > piece.ly <<'EOF'
\version "2.24.1"

\header {
  title = "Procedural Chamber Piece"
  composer = "generated"
  tagline = ##f
}

global = {
  \key g \major
  \time 4/4
  \tempo 4 = 96
}

violinOne = \relative c'' {
  \global
  \repeat unfold 8 {
    g4 b d g |
    fis4 d b a |
    g4 b d g |
    a4 g fis d |
  }
}

violinTwo = \relative c'' {
  \global
  \repeat unfold 8 {
    d4 g b d |
    d4 b g fis |
    d4 g b d |
    d4 b a fis |
  }
}

viola = \relative c' {
  \global
  \repeat unfold 8 {
    b4 d g b |
    a4 fis d b |
    b4 d g b |
    c4 a fis d |
  }
}

cello = \relative c {
  \global
  \repeat unfold 8 {
    g2 d |
    e2 b |
    c2 g |
    d2 d |
  }
}

flute = \relative c''' {
  \global
  \repeat unfold 8 {
    g8 a b d g4 d |
    fis8 g a fis d4 a |
    g8 a b d g4 d |
    a8 b c a fis4 d |
  }
}

clarinet = \relative c'' {
  \global
  \repeat unfold 8 {
    b4 g d' b |
    a4 fis d a |
    b4 g d' b |
    c4 a fis d |
  }
}

\score {
  <<
    \new Staff \with { midiInstrument = "violin" } \violinOne
    \new Staff \with { midiInstrument = "violin" } \violinTwo
    \new Staff \with { midiInstrument = "viola" } \viola
    \new Staff \with { midiInstrument = "cello" } \cello
    \new Staff \with { midiInstrument = "flute" } \flute
    \new Staff \with { midiInstrument = "clarinet" } \clarinet
  >>
  \layout { }
  \midi { }
}
EOF

# Compile with LilyPond
lilypond piece.ly

# Convert MIDI → WAV
timidity piece.midi -Ow -o piece.wav

# Convert WAV → MP3
ffmpeg -y -i piece.wav -codec:a libmp3lame -qscale:a 2 piece.mp3

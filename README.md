# Chiptune Extension and Generation using Markov Chains

## Background
This course project, completed in Spring 2022, surveyed and implemented chiptune/8-bit track extension and generation using Markov chain techniques. Starting in April 2022, this project moved towards open source development in order to refine its various components.

Course project group members:
[Oscar Sandford](https://github.com/oscarsandford), [Colson Demedeiros](https://github.com/Colslaw0), [Jae Park](https://github.com/jpark052)

## Structure
* `/report`: LaTeX and resources for compiling the written report. Closed.
* `/src` : Implementation source code and notebooks. See subdirectory README for more info.

## Planned Improvements

- [ ] Enhance GUI
  - More aesthetic, features to allow higher-fidelity interaction with API
- [ ] Solve syncing issue
  - Issues with tracks not being combined in sync with the original
- [ ] Instrument mappings
  - Map notes to different waveform types based on instrument labels
- [ ] Make mcc-parser more robust
  - Handle complex MIDI message types without failure
- [ ] Make waveform generation more efficient
  - Caching repeating RTTTL notes
- [ ] Explore methods for quantitative evaluation
  - Cross-similarity
